from odoo import _, fields, models
from odoo.exceptions import UserError


class UpdateWarehouseWizard(models.TransientModel):
    _name = "update.warehouse.wizard"
    _description = "Update Warehouse Wizard"

    location_id = fields.Many2one(
        "stock.location", required=True, string="Stock Location", domain="[('usage', '=', 'internal')]"
    )
    current_location_id = fields.Many2many("stock.location", string="Current Location")
    stock_picking_ids = fields.Many2many("stock.picking")

    def confirm(self):
        loc = self.stock_picking_ids.filtered(lambda l: l.location_id).mapped("location_id")
        state = self.stock_picking_ids.filtered(lambda l: l.state).mapped("state")
        operation_delivery = self.stock_picking_ids.filtered(lambda l: l.picking_type_id).mapped("picking_type_id")
        if loc:
            count_location = 0
            for val in loc:
                count_location += 1
        if count_location > 1:
            raise UserError(_("Stock Location of Selected records should be same."))
        if state:
            for line in state:
                if line == "done" or line == "cancel":
                    raise UserError(_("Selected records should not be in Done state or Cancel state."))
        for result in operation_delivery:
            if result.code != "outgoing":
                raise UserError(_("Selected records Operation Type should be in Delivery."))
        if self.location_id:
            for res in self.stock_picking_ids:
                for val in res.move_line_ids_without_package:
                    val.update(
                        {
                            "location_id": self.location_id,
                        }
                    )
                res.update(
                    {
                        "location_id": self.location_id,
                        "picking_type_id": self.location_id.warehouse_id.out_type_id.id,
                    }
                )
