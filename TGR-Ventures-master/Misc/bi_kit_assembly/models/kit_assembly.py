from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError
import datetime


class KitAssembly(models.Model):
    _name = "kit.assembly"
    _description = "Kit Assembly"
    _rec_name = "product_id"

    product_id = fields.Many2one("product.product", string="Product")
    quantity = fields.Float("Quantity")
    uom_id = fields.Many2one("uom.uom", string="Unit")
    bom_id = fields.Many2one("bill.material", string="Kit Specification")
    reference = fields.Char("Reference")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    location_id = fields.Many2one("stock.location", string="Location")
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company.id)
    kit_line_ids = fields.One2many("kit.assembly.lines", "kit_assembly_id")
    date = fields.Date("Date", default=date.today())
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approve", "Approve"),
            ("done", "Done"),
        ],
        string="State",
    )
    assembly_count = fields.Integer(string="Moves", compute="_compute_assembly_count")
    journal_count = fields.Integer(string="Entries", compute="_compute_journal_count")
    is_done = fields.Boolean("is_done", default=False, copy=False)
    is_disassembly = fields.Boolean("is_disassembly", default=False, copy=False)
    available_quantity = fields.Float("Available Quantity", compute="_compute_available_quantity")
    available_quantity_uom_id = fields.Many2one("uom.uom", string="Unit")

    @api.depends("product_id", "location_id")
    def _compute_available_quantity(self):
        for rec in self:
            rec.available_quantity = rec.product_id.with_context(location=rec.location_id.id).qty_available

    @api.onchange("product_id")
    def _onchange_product_id_uom(self):
        if self.product_id:
            if self.product_id.uom_id:
                self.uom_id = self.product_id.uom_id.id
                self.available_quantity_uom_id = self.product_id.uom_id.id

    @api.onchange("warehouse_id")
    def _onchange_warehouse_id(self):
        if self.warehouse_id:
            self.location_id = self.warehouse_id.lot_stock_id.id

    def unlink(self):
        for each in self:
            if each.state == "done":
                raise UserError(_("You cannot delete this Record."))
        return super(KitAssembly, self).unlink()

    def action_approve(self):
        self.state = "approve"

    def action_done_assembly(self):
        for assembly in self:
            for line in assembly.kit_line_ids.filtered(lambda rline: rline.line_quantity > 0):
                if line.product_id.tracking == "serial":
                    if line.line_quantity < len(line.mapped("serial_ids")):
                        raise UserError(
                            _(f"You can enter only {line.line_quantity} serial numbers for {line.product_id.name}.")
                        )
                    elif line.line_quantity > len(line.mapped("serial_ids")):
                        raise UserError(_(f"Enter serial number for all {line.line_quantity} {line.product_id.name}."))

                elif line.product_id.tracking == "lot":
                    if line.mapped("serial_ids"):
                        total_lot_capacity = 0
                        for check in line.mapped("serial_ids"):
                            if check.serial_quantity == 0:
                                raise UserError(_("Enter the quantity for all lots."))
                        total_actual_qty = line.line_quantity
                        serial_qty = sum(line.mapped("serial_ids").mapped("serial_quantity"))
                        if total_actual_qty != serial_qty:
                            raise UserError(_(f"Incorrect Quantity for {line.product_id.name}"))
                        for each_lot in line.mapped("serial_ids").mapped("serial_id"):
                            total_lot_capacity += line.product_id.with_context(
                                {
                                    "to_date": datetime.datetime.now(),
                                    "lot_id": each_lot.id,
                                    "location_id": line.kit_assembly_id.location_id.id,
                                }
                            ).qty_available
                        if line.line_quantity > total_lot_capacity:
                            raise UserError(
                                _(
                                    f"Return quantity {line.line_quantity} for {line.product_id.name}"
                                    f" is greater than the available quantity in given lots."
                                )
                            )
                    else:
                        raise UserError(_(f"Enter lot number for all {line.line_quantity} {line.product_id.name}."))

            for line in assembly.kit_line_ids.filtered(lambda rline: rline.line_quantity > 0):
                transfer_name = ""
                picking_type = self.env["stock.picking.type"].search([("code", "=", "mrp_operation")], limit=1).id
                if assembly.is_disassembly:
                    dest_location = assembly.location_id.id
                    from_location = self.env["stock.location"].search([("usage", "=", "production")], limit=1).id
                    transfer_name = f"{line.product_id.name} - Disassembly"
                    template = {
                        "name": transfer_name,
                        "product_id": line.product_id.id,
                        "product_uom_qty": line.line_quantity,
                        "product_uom": line.line_uom_id.id,
                        "location_id": from_location,
                        "location_dest_id": dest_location,
                        "state": "draft",
                        "assembly_id": assembly.id,
                    }
                else:
                    from_location = assembly.location_id.id
                    dest_location = self.env["stock.location"].search([("usage", "=", "production")], limit=1).id
                    transfer_name = f"{line.product_id.name} - Assembly"
                    template = {
                        "name": transfer_name,
                        "product_id": line.product_id.id,
                        "product_uom_qty": line.line_quantity,
                        "product_uom": line.line_uom_id.id,
                        "location_id": from_location,
                        "location_dest_id": dest_location,
                        "picking_type_id": picking_type,
                        "state": "draft",
                        "assembly_id": assembly.id,
                    }
                move_id = self.env["stock.move"].sudo().create(template)
                move_id._action_confirm()
                move_id._action_assign()

                for line_moves in move_id.filtered(lambda rline: rline.product_uom_qty > 0):
                    stock_move_line = self.env["stock.move.line"].search([("move_id", "=", move_id.id)])
                    if line_moves.product_id.tracking != "none":
                        if line_moves.product_id.tracking == "serial":
                            serial_ids = line.serial_ids.mapped("serial_id")
                            moveline = stock_move_line.filtered(
                                lambda mv_line: mv_line.product_id == line_moves.product_id
                                and mv_line.move_id == move_id
                                and mv_line.product_id.tracking == "serial"
                            )
                            if moveline:
                                for x in range(0, len(serial_ids)):
                                    moveline[x].lot_id = serial_ids[x]
                                    moveline[x].qty_done = 1
                            else:
                                raise UserError(_("Incorrect Values"))
                        elif line_moves.product_id.tracking == "lot":
                            qty = line_moves.product_uom_qty
                            moveline = stock_move_line.filtered(
                                lambda mv_line: mv_line.product_id == line_moves.product_id
                                and mv_line.move_id == move_id
                                and mv_line.product_id.tracking == "lot"
                            )
                            if moveline:
                                for lot in line.serial_ids.mapped("serial_id"):
                                    lot_qty = line.product_id.with_context(
                                        {
                                            "to_date": datetime.datetime.now(),
                                            "lot_id": lot.id,
                                            "location_id": assembly.location_id.id,
                                        }
                                    ).qty_available
                                    if qty > lot_qty:
                                        moveline_qty = lot_qty
                                        qty -= moveline_qty
                                    else:
                                        moveline_qty = qty
                                    if not moveline.lot_id:
                                        moveline.lot_id = lot.id
                                        moveline.qty_done = moveline_qty
                                    else:
                                        moveline.copy(
                                            {
                                                "lot_id": lot.id,
                                                "qty_done": moveline_qty,
                                            }
                                        )
                            else:
                                raise UserError(_("Incorrect Values"))
                    else:
                        moveline = stock_move_line.filtered(
                            lambda mv_line: mv_line.product_id == line_moves.product_id
                            and mv_line.move_id == move_id
                            and mv_line.product_id.tracking == "none"
                        )
                        moveline.qty_done = line_moves.product_uom_qty
                for rec in move_id.move_line_nosuggest_ids:
                    rec._onchange_serial_number()
                move_id._onchange_move_line_ids()
                move_id._action_done()
            if assembly.is_disassembly:
                finished = {
                    "name": transfer_name,
                    "product_id": assembly.product_id.id,
                    "product_uom_qty": assembly.quantity,
                    "product_uom": assembly.uom_id.id,
                    "location_id": dest_location,
                    "location_dest_id": from_location,
                    # "picking_type_id": picking_type,
                    "assembly_id": assembly.id,
                    "state": "draft",
                }
            else:
                finished = {
                    "name": transfer_name,
                    "product_id": assembly.product_id.id,
                    "product_uom_qty": assembly.quantity,
                    "product_uom": assembly.uom_id.id,
                    "location_id": dest_location,
                    "location_dest_id": from_location,
                    "assembly_id": assembly.id,
                    "state": "draft",
                }
            finished_move_id = self.env["stock.move"].sudo().create(finished)
            finished_move_id._action_confirm()
            finished_move_id._action_assign()
            for move_line_id in finished_move_id.move_line_ids:
                move_line_id.write(
                    {
                        "qty_done": finished_move_id.product_uom_qty,
                        "location_id": dest_location,
                    }
                )
            finished_move_id._onchange_move_line_ids()
            finished_move_id._action_done()
            assembly.is_done = True
            assembly.state = "done"

    def _compute_assembly_count(self):
        for rec in self:
            assembly_count = self.env["stock.move"].search_count([("assembly_id", "=", rec.id)])
            rec.assembly_count = assembly_count

    def view_assembly_moves(self):
        assembly_ids = self.env["stock.move"].search([("assembly_id", "=", self.id)])
        if len(assembly_ids) > 0:
            return {
                "name": _("Moves"),
                "type": "ir.actions.act_window",
                "res_model": "stock.move",
                "view_mode": "tree,form",
                "domain": [("id", "in", assembly_ids.ids)],
                "target": "current",
            }

    def _compute_journal_count(self):
        for rec in self:
            journal_count = self.env["account.move"].search_count([("assembly_id", "=", rec.id)])
            rec.journal_count = journal_count

    def view_journal_entry(self):
        journal_ids = self.env["account.move"].search([("assembly_id", "=", self.id)])
        if len(journal_ids) > 0:
            return {
                "name": _("Entries"),
                "type": "ir.actions.act_window",
                "res_model": "account.move",
                "view_mode": "tree,form",
                "domain": [("id", "in", journal_ids.ids)],
                "target": "current",
            }

    @api.model
    def create(self, vals):
        res = super(KitAssembly, self).create(vals)
        for rec in res:
            rec.state = "draft"
        return res

    @api.onchange("bom_id")
    def _onchange_bom_id(self):
        new_lines = []
        if self.bom_id:
            self.product_id = self.bom_id.product_id.id
            if self.kit_line_ids:
                self.kit_line_ids = False
            for each in self.bom_id.bom_line_ids:
                new_lines.append(
                    (
                        0,
                        0,
                        {
                            "product_id": each.product_id.id,
                            "line_quantity": each.line_quantity,
                            "line_uom_id": each.line_uom_id.id,
                            "kit_assembly_id": self.id,
                            "is_no_track": each.is_no_track,
                        },
                    )
                )
            vals = {
                "quantity": self.bom_id.quantity,
                "kit_line_ids": new_lines,
            }
            self.sudo().write(vals)
            self.kit_line_ids._onchange_uom_product_id()


class KitAssemblyLine(models.Model):
    _name = "kit.assembly.lines"
    _description = "Kit Assembly Lines"

    kit_assembly_id = fields.Many2one("kit.assembly", string="Kit Assembly")
    product_id = fields.Many2one("product.product", string="Product")
    line_quantity = fields.Float("Quantity")
    line_uom_id = fields.Many2one("uom.uom", string="UoM")
    unit_cost = fields.Float("Unit Cost", related="product_id.standard_price")
    serial_ids = fields.One2many("kit.serial", "kit_serial_line_id", string="Serial")
    is_no_track = fields.Boolean("is_no_track", default=False, copy=False)
    product_sku = fields.Char("SKU", related="product_id.default_code")

    def action_show_serial(self):
        self.ensure_one()
        view = self.env.ref("bi_kit_assembly.serial_line_tracking_view_form")
        return {
            "name": _("Tracking"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "kit.assembly.lines",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
        }

    @api.onchange("product_id")
    def _onchange_uom_product_id(self):
        for line in self:
            if line.product_id:
                if line.product_id.uom_id:
                    line.line_uom_id = line.product_id.uom_id.id
            if line.product_id.tracking == "none":
                line.is_no_track = True
            else:
                line.is_no_track = False

    @api.onchange("serial_ids", "line_quantity")
    def _onchange_serial_ids(self):
        for each in self:
            if each.product_id.tracking == "serial":
                if each.line_quantity < len(each.mapped("serial_ids")):
                    raise UserError(_("Serial Number Exceeded"))

    class ProductKitSerial(models.Model):
        _name = "kit.serial"
        _description = "Kit Serial ID"

        kit_serial_line_id = fields.Many2one("kit.assembly.lines", string="")
        serial_quantity = fields.Integer("Quantity")
        serial_id = fields.Many2one("stock.production.lot", string="Serial number", required=True)
        is_lot = fields.Boolean("is_lot_track", default=False, copy=False, compute="_compute_is_lot")

        def _compute_is_lot(self):
            for line in self:
                if line.kit_serial_line_id.product_id.tracking == "lot":
                    line.is_lot = True
                else:
                    line.is_lot = False

        @api.onchange("serial_id")
        def _onchange_serial_id(self):
            serial_ids = self.kit_serial_line_id.serial_ids.mapped("serial_id").ids
            for each in self:
                if each.kit_serial_line_id.product_id.tracking == "lot":
                    total_actual_qty = each.kit_serial_line_id.line_quantity
                    serial_qty = sum(self.mapped("serial_quantity"))
                    if total_actual_qty < serial_qty:
                        raise UserError(_("Quantity Exceeded"))
                    lot_qty = each.kit_serial_line_id.product_id.with_context(
                        {
                            "to_date": datetime.datetime.now(),
                            "lot_id": each.id,
                            "location_id": self.kit_serial_line_id.kit_assembly_id.location_id.id,
                        }
                    ).qty_available
                    if each.serial_quantity > lot_qty:
                        raise UserError(
                            _(
                                f"Quantity {each.serial_quantity} for {each.kit_serial_line_id.product_id.name}"
                                f" is greater than the available quantity in given lots."
                            )
                        )
            return {
                "domain": {
                    "serial_id": [
                        ("product_id", "=", self.kit_serial_line_id.product_id.id),
                        ("id", "not in", serial_ids),
                    ]
                }
            }
