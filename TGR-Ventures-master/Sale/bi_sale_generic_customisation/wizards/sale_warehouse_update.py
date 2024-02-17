from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleWarehouseUpdate(models.TransientModel):
    _name = "sale.warehouse.update"
    _description = "Sale warehouse update"

    warehouse_id = fields.Many2one("stock.warehouse", required=True, string="Stock Location")
    current_warehouse_ids = fields.Many2many("stock.warehouse", string="Current Location")
    sale_ids = fields.Many2many("sale.order")

    def confirm(self):
        state = self.sale_ids.picking_ids.filtered(lambda l: l.state).mapped("state")
        if any(state) in ["done", "cancel"]:
            raise UserError(_("Warehouse cannot be switched for delivery order in 'done' or 'cancel' state."))
        if self.warehouse_id:
            for sale in self.sale_ids:
                for res in sale.picking_ids:
                    for val in res.move_line_ids_without_package:
                        val.update(
                            {
                                "location_id": self.warehouse_id.lot_stock_id.id,
                            }
                        )
                    res.update(
                        {
                            "location_id": self.warehouse_id.lot_stock_id.id,
                            "picking_type_id": self.warehouse_id.out_type_id.id,
                        }
                    )
                sale.update(
                    {
                        "warehouse_id": self.warehouse_id.id,
                    }
                )
