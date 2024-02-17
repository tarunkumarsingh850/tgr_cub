from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class MaterialRequest(models.Model):
    _name = "material.request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Internal Material Request"

    user_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    name = fields.Char("Sequence", default="New", copy=False, index=True)
    reference = fields.Char(string="Reference", tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("cancel", "Cancelled"),
            ("waiting", "Waiting For Approval"),
            ("approved", "Approved"),
            ("done", "Done"),
            ("return", "Returned"),
        ],
        string="Status",
        index=True,
        default="draft",
        store=True,
        tracking=True,
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed\n"
        " * Cancelled: has been cancelled, can't be confirmed anymore",
    )
    requested_from = fields.Many2one(
        "stock.warehouse",
        string="Requested to",
        tracking=True,
    )
    requested_to = fields.Many2one(
        "stock.warehouse",
        string="Requested From",
        tracking=True,
    )
    transfer_date = fields.Datetime(string="Scheduled Date", required=True, tracking=True, default=fields.Datetime.now)
    material_line_ids = fields.One2many("material.request.line", "material_id", string="Material Request Line")
    picking_type_id = fields.Many2one("stock.picking.type", string="Stock Picking Type", tracking=True)
    transfer_reference_id = fields.Many2one(
        "stock.picking", string="Transfer Reference", readonly=True, copy=False, tracking=True
    )
    second_transfer_id = fields.Many2one("stock.picking", readonly=True, copy=False, tracking=True)
    return_transfer_id = fields.Many2one("stock.picking", readonly=True, copy=False, tracking=True)
    transfer = fields.Char(string="Transfer")
    intransit = fields.Boolean("In Transit", default=False, tracking=True)
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company, required=True, readonly=True
    )
    direct_transfer = fields.Boolean(string="Direct Transfer", default=False)
    created_user_id = fields.Many2one("res.users", string="User", default=lambda self: self.env.user.id)

    @api.onchange("requested_to")
    def onchange_requested_to(self):
        if self.requested_to:
            if self.requested_from and self.requested_from == self.requested_to:
                raise UserError(_("You cannot choose same Warehouse"))
            self.picking_type_id = self.requested_to.int_type_id.id

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            if "company_id" in vals:
                vals["name"] = self.env["ir.sequence"].with_context(force_company=vals["company_id"]).next_by_code(
                    "material.request.new"
                ) or _("New")
            else:
                vals["name"] = self.env["ir.sequence"].next_by_code("material.request.new") or _("New")

        result = super(MaterialRequest, self).create(vals)
        for lines in result.material_line_ids:
            if lines.product_id and result.requested_to:
                opening_qty = lines.product_id.with_context(
                    {"loaction": result.requested_to.lot_stock_id.id, "to_date": datetime.now()}
                ).free_qty
                if lines.quantity > opening_qty:
                    raise UserError(
                        _("%s has only %s quantities in Source location.") % (lines.product_id.name, opening_qty)
                    )
        return result

    def unlink(self):
        for transfer in self:
            if transfer.state not in ("draft", "cancel"):
                raise UserError(_("Cannot delete transfer which are already confirmed."))
        return super(MaterialRequest, self).unlink()

    def do_confirm(self):
        if not self.picking_type_id:
            raise UserError(_("No picking type found."))
        for line in self.material_line_ids:
            line.quantity_done = line.quantity
        self.write({"state": "waiting"})

    def do_cancel(self):
        self.write({"state": "draft"})

    def approve_product(self):
        transit = (
            self.env["stock.location"]
            .sudo()
            .search([("usage", "=", "transit"), ("company_id", "=", self.company_id.id)], limit=1)
        )
        if not transit:
            raise UserError(_("No transit location found."))
        location = self.requested_to.lot_stock_id
        picking_obj = self.picking_type_id.id
        for vals in self:
            pick = {
                "origin": vals.name,
                "picking_type_id": picking_obj,
                "location_id": location.id,
                "location_dest_id": transit.id,
                "scheduled_date": vals.transfer_date,
                "company_id": vals.company_id.id,
            }
        picking = self.env["stock.picking"].sudo().create(pick)
        for line in self.material_line_ids:
            if line.product_id:
                if line.lot_ids and line.quantity_done > sum(line.lot_ids.mapped("product_qty")):
                    raise UserError(
                        _("You cannot transfer %s more than available lot quantity.") % line.product_id.name
                    )
                move = {
                    "name": vals.name,
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.quantity_done,
                    "product_uom": line.unit_of_measure.id,
                    "location_id": location.id,
                    "location_dest_id": transit.id,
                    "picking_id": picking.id,
                    "company_id": vals.company_id.id,
                    "mat_transfer_line_id": line.id,
                }
                self.env["stock.move"].sudo().create(move)
        picking.sudo().action_assign()
        self.transfer_reference_id = picking.id
        transfer = self.env["stock.immediate.transfer"].create(
            {
                "pick_ids": [(4, picking.id)],
                "immediate_transfer_line_ids": [(0, 0, {"to_immediate": True, "picking_id": picking.id})],
            }
        )
        transfer.with_context(button_validate_picking_ids=picking.id).process()
        self.transfer = self.transfer_reference_id.name
        self.write({"state": "approved"})

    def return_stock(self):
        transit = (
            self.env["stock.location"]
            .sudo()
            .search([("usage", "=", "transit"), ("company_id", "=", self.company_id.id)], limit=1)
        )
        if not transit:
            raise UserError(_("No transit location found."))
        location = self.requested_to.lot_stock_id
        picking_obj = self.picking_type_id.id
        for vals in self:
            pick = {
                "origin": vals.name,
                "picking_type_id": picking_obj,
                "location_id": transit.id,
                "location_dest_id": location.id,
                "scheduled_date": vals.transfer_date,
                "company_id": vals.company_id.id,
            }
        picking = self.env["stock.picking"].sudo().create(pick)
        for line in self.material_line_ids:
            if line.product_id:
                move = {
                    "name": vals.name,
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.quantity_done,
                    "product_uom": line.unit_of_measure.id,
                    "location_id": transit.id,
                    "location_dest_id": location.id,
                    "picking_id": picking.id,
                    "company_id": vals.company_id.id,
                    "mat_transfer_line_id": line.id,
                }
                self.env["stock.move"].sudo().create(move)
        picking.sudo().action_assign()
        self.return_transfer_id = picking.id
        transfer = self.env["stock.immediate.transfer"].create(
            {
                "pick_ids": [(4, picking.id)],
                "immediate_transfer_line_ids": [(0, 0, {"to_immediate": True, "picking_id": picking.id})],
            }
        )
        transfer.with_context(button_validate_picking_ids=picking.id).process()
        self.write({"state": "return"})

    def do_approve(self):
        location_to = self.requested_to.lot_stock_id
        for line in self.material_line_ids:
            if line.product_id:
                if line.product_id.with_context({"location": location_to.id}).sudo().free_qty < 0:
                    raise UserError(_("Material %s is not available") % line.product_id.name)
                elif line.quantity_done > line.product_id.with_context({"location": location_to.id}).sudo().free_qty:
                    raise UserError(
                        _("%s Available quantity is %s")
                        % (
                            line.product_id.name,
                            line.product_id.with_context({"location": self.requested_to.lot_stock_id.id}).free_qty,
                        )
                    )
        self.approve_product()

    def done_transfer(self):
        transit = (
            self.env["stock.location"]
            .sudo()
            .search([("usage", "=", "transit"), ("company_id", "=", self.company_id.id)], limit=1)
        )
        location_dest = self.requested_from.lot_stock_id
        picking_obj = self.picking_type_id.id
        for vals in self:
            pick = {
                "origin": vals.transfer,
                "picking_type_id": picking_obj,
                "location_id": transit.id,
                "location_dest_id": location_dest.id,
                "scheduled_date": vals.transfer_date,
                "company_id": vals.company_id.id,
            }
        picking = self.env["stock.picking"].sudo().create(pick)
        for line in self.material_line_ids:
            if line.product_id:
                move = {
                    "name": vals.transfer,
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.quantity_done,
                    "product_uom": line.unit_of_measure.id,
                    "location_id": transit.id,
                    "location_dest_id": location_dest.id,
                    "picking_id": picking.id,
                    "company_id": vals.company_id.id,
                    "mat_transfer_line_id": line.id,
                }
                self.env["stock.move"].sudo().create(move)
        picking.sudo().action_assign()
        self.second_transfer_id = picking.id
        transfer = self.env["stock.immediate.transfer"].create(
            {
                "pick_ids": [(4, picking.id)],
                "immediate_transfer_line_ids": [(0, 0, {"to_immediate": True, "picking_id": picking.id})],
            }
        )
        transfer.with_context(button_validate_picking_ids=picking.id).process()
        self.write({"state": "done"})


class MaterialRequestLine(models.Model):
    _name = "material.request.line"

    product_id = fields.Many2one("product.product")
    tracking = fields.Selection(related="product_id.tracking")
    quantity = fields.Float(string="Intial Demand", default=1.0)
    quantity_done = fields.Float(string="Quantity Delivered", default=0.0)
    unit_of_measure = fields.Many2one("uom.uom", string="Unit Of Measure")
    product_cost = fields.Float(string="Cost")
    product_unit_price = fields.Float(string="Unit Price")
    lot_ids = fields.Many2many("stock.production.lot", string="Serial Numbers")
    domain_lot_ids = fields.Many2many(
        "stock.production.lot",
        "material_request_line_lot_domain_rel",
        string="Serial Numbers",
        compute="_compute_domain_lot_ids",
    )
    material_id = fields.Many2one("material.request", string="Material Request")

    @api.depends("product_id")
    def _compute_domain_lot_ids(self):
        for line in self:
            if line.product_id:
                lots = self.env["stock.production.lot"].search(
                    [("product_id", "=", line.product_id.id), ("company_id", "=", line.material_id.company_id.id)]
                )
                quants = lots.quant_ids.filtered(
                    lambda q: q.quantity != 0 and q.location_id == line.material_id.requested_to.lot_stock_id
                )
                line.domain_lot_ids = quants.mapped("lot_id")
            else:
                line.domain_lot_ids = False

    @api.onchange("lot_ids")
    def _onchange_lot_ids(self):
        for line in self:
            if line.product_id.tracking == "serial":
                line.quantity_done = sum(line.lot_ids.mapped("product_qty"))

    @api.onchange("quantity_done")
    def _onchange_quantity_done(self):
        if self.product_id and self.quantity_done > self.quantity:
            raise UserError(
                _("You have processed more than what was initially planned for the product %s" % (self.product_id.name))
            )

    @api.onchange("product_id")
    def onchange_product_id(self):
        for vals in self:
            if vals.product_id:
                vals.unit_of_measure = vals.product_id.uom_id
                vals.product_cost = vals.product_id.standard_price
                vals.product_unit_price = vals.product_id.list_price
