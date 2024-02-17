from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    warehouse_id = fields.Many2one(
        "stock.warehouse", string="Warehouse", copy=False, compute="_compute_warehouse", store=True
    )

    @api.depends("usage")
    def _compute_warehouse(self):
        for each in self:
            warehouse_id = self.env["stock.warehouse"].search([("lot_stock_id", "=", each.id)])
            if warehouse_id:
                each.warehouse_id = warehouse_id.id
            else:
                each.warehouse_id = False
