from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError
import datetime


class PackageManagement(models.Model):
    _name = "packet.management"
    _description = "Packet Management"
    _rec_name = "product_id"

    name = fields.Char("Name", default="New", copy=False)
    product_id = fields.Many2one("product.product", string="Product")
    quantity = fields.Float("Quantity")
    uom_id = fields.Many2one("uom.uom", string="Unit")
    reference = fields.Char("Reference")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    location_id = fields.Many2one("stock.location", string="Location")
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company.id)
    packet_line_ids = fields.One2many("packet.management.lines", "packet_id")
    date = fields.Date("Date", default=date.today())
    serial_id = fields.Many2one("stock.production.lot", string="Lot", required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approve", "Approve"),
            ("done", "Done"),
        ],
        string="State",
    )
    packet_count = fields.Integer(string="Moves", compute="_compute_packet_count")
    journal_count = fields.Integer(string="Entries", compute="_compute_journal_count")

    @api.onchange("product_id")
    def _onchange_product_id_uom(self):
        if self.product_id:
            if self.product_id.uom_id:
                self.uom_id = self.product_id.uom_id.id

    @api.onchange("serial_id", "product_id", "location_id")
    def _onchange_onhand_qty(self):
        self.quantity = 0.0
        if self.product_id:
            if self.serial_id:
                self.quantity = self.product_id.with_context(
                    {"lot_id": self.serial_id.id, "location": self.location_id.id, "to_date": datetime.datetime.now()}
                ).qty_available

    @api.onchange("warehouse_id")
    def _onchange_warehouse_id(self):
        if self.warehouse_id:
            self.location_id = self.warehouse_id.lot_stock_id.id

    def unlink(self):
        for each in self:
            if each.state == "done":
                raise UserError(_("You cannot delete this Record."))
        return super(PackageManagement, self).unlink()

    def action_approve(self):
        for line in self.packet_line_ids.filtered(lambda rline: rline.line_quantity > 0):
            lot_master = self.env["stock.production.lot"]
            sequences = self.env["ir.sequence"].search(
                [("company_id", "=", self.company_id.id), ("name", "=", self.serial_id.name)]
            )
            if not sequences:
                sequence_obj = (
                    self.env["ir.sequence"]
                    .sudo()
                    .create(
                        {
                            "company_id": self.company_id.id,
                            "padding": 3,
                            "name": self.serial_id.name,
                        }
                    )
                )
                end_code = sequence_obj.next_by_id(sequence_obj.id)
            else:
                end_code = sequences.next_by_id(sequences.id)

            form_lot = f"{self.serial_id.name}/{end_code}"
            new_lot = lot_master.create(
                {"name": form_lot, "product_id": line.product_id.id, "company_id": self.company_id.id}
            )
            line.lot_id = new_lot.id
        self.state = "approve"

    def action_done(self):
        transfer_name = ""
        for line in self.packet_line_ids.filtered(lambda rline: rline.line_quantity > 0):
            picking_type = self.env["stock.picking.type"].search([("code", "=", "mrp_operation")], limit=1).id
            from_location = self.env["stock.location"].search([("usage", "=", "inventory")], limit=1).id
            dest_location = self.location_id.id
            transfer_name = f"{line.product_id.name} - Packet Management"
            template = {
                "name": transfer_name,
                "product_id": line.product_id.id,
                "product_uom_qty": line.line_quantity,
                "product_uom": line.line_uom_id.id,
                "location_id": from_location,
                "location_dest_id": dest_location,
                "state": "draft",
                "packet_id": self.id,
            }

            move_id = self.env["stock.move"].sudo().create(template)
            move_id._action_confirm()
            move_id._action_assign()

            for line_moves in move_id.filtered(lambda rline: rline.product_uom_qty > 0):
                stock_move_line = self.env["stock.move.line"].search([("move_id", "=", move_id.id)])
                if line_moves.product_id.tracking != "none":
                    if line_moves.product_id.tracking == "serial":
                        raise UserError(_("Please select Lot Product"))
                    elif line_moves.product_id.tracking == "lot":
                        moveline = stock_move_line.filtered(
                            lambda mv_line: mv_line.product_id == line_moves.product_id
                            and mv_line.move_id == move_id
                            and mv_line.product_id.tracking == "lot"
                        )
                        if moveline:
                            for lot in line.lot_id:
                                if not moveline.lot_id:
                                    moveline.lot_id = lot.id
                                    moveline.qty_done = line_moves.product_uom_qty
                                else:
                                    moveline.copy(
                                        {
                                            "lot_id": lot.id,
                                            "qty_done": line_moves.product_uom_qty,
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
            move_id._action_done()
        from_location = self.location_id.id
        dest_location = self.env["stock.location"].search([("usage", "=", "inventory")], limit=1).id
        transfer_name = f"{self.product_id.name} - Packet Moves"
        finished = {
            "name": transfer_name,
            "product_id": self.product_id.id,
            "product_uom_qty": sum(self.packet_line_ids.mapped("line_quantity")),
            "product_uom": self.uom_id.id,
            "location_id": from_location,
            "location_dest_id": dest_location,
            "picking_type_id": picking_type,
            "packet_id": self.id,
            "state": "draft",
        }

        finished_move_id = self.env["stock.move"].sudo().create(finished)
        finished_move_id._action_confirm()
        finished_move_id._action_assign()
        for move_line_id in finished_move_id.move_line_ids:
            move_line_id.write(
                {
                    "lot_id": self.serial_id.id,
                    "qty_done": finished_move_id.product_uom_qty,
                    "location_id": from_location,
                }
            )
        finished_move_id._onchange_move_line_ids()
        finished_move_id._action_done()
        self.state = "done"

    def _compute_packet_count(self):
        for rec in self:
            packet_count = self.env["stock.move"].search_count([("packet_id", "=", rec.id)])
            rec.packet_count = packet_count

    def view_packet_moves(self):
        packet_ids = self.env["stock.move"].search([("packet_id", "=", self.id)])
        if len(packet_ids) > 0:
            return {
                "name": _("Moves"),
                "type": "ir.actions.act_window",
                "res_model": "stock.move",
                "view_mode": "tree,form",
                "domain": [("id", "in", packet_ids.ids)],
                "target": "current",
            }

    def _compute_journal_count(self):
        for rec in self:
            journal_count = self.env["account.move"].search_count([("packet_id", "=", rec.id)])
            rec.journal_count = journal_count

    def view_journal_entry(self):
        journal_ids = self.env["account.move"].search([("packet_id", "=", self.id)])
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
        res = super(PackageManagement, self).create(vals)
        for rec in res:
            rec.state = "draft"
        total_qty = 0
        if res.packet_line_ids:
            for lines in res.packet_line_ids:
                total_qty += lines.line_quantity
            if total_qty > res.quantity:
                raise UserError(_("Quantity limit exceeded!!!"))
        sequences = self.env["ir.sequence"].search(
            [("company_id", "=", res.company_id.id), ("name", "=", "Packet Management")]
        )
        if not sequences:
            sequence_obj = (
                self.env["ir.sequence"]
                .sudo()
                .create(
                    {
                        "company_id": res.company_id.id,
                        "padding": 5,
                        "name": "Packet Management",
                    }
                )
            )
            end_code = sequence_obj.next_by_id(sequence_obj.id)
        else:
            end_code = sequences.next_by_id(sequences.id)

        res.name = f"PM-{end_code}"
        return res

    def write(self, values):
        rec = super(PackageManagement, self).write(values)
        total_qty = 0
        if self.packet_line_ids:
            for lines in self.packet_line_ids:
                total_qty += lines.line_quantity
            if total_qty > self.quantity:
                raise UserError(_("Mismatch in Quantities"))
        return rec


class PackageManagementLine(models.Model):
    _name = "packet.management.lines"
    _description = "Packet Management Lines"

    packet_id = fields.Many2one("packet.management", string="Packet Management")
    product_id = fields.Many2one(
        "product.product",
        string="Product",
    )
    pack_description = fields.Char("Pack Size Description", related="product_id.product_tmpl_id.pack_size_desc")
    line_quantity = fields.Float("Quantity")
    line_uom_id = fields.Many2one("uom.uom", string="UoM")
    lot_id = fields.Many2one("stock.production.lot", string="Lot")

    @api.onchange("product_id")
    def _onchange_uom_product_id(self):
        for line in self:
            if line.product_id:
                if line.product_id.uom_id:
                    line.line_uom_id = line.product_id.uom_id.id
