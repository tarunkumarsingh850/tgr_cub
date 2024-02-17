from odoo import fields, models


class ProductScrap(models.Model):
    _inherit = "stock.scrap"

    reason_code_id = fields.Many2one("reason.code", string="Reason Code")
    stock_onhand_quantity = fields.Float("Available Quantity", compute="_compute_stock_quantity")

    def _compute_stock_quantity(self):
        product_qty = self.product_id.with_context({"location": self.location_id.id}).free_qty
        self.stock_onhand_quantity = product_qty
