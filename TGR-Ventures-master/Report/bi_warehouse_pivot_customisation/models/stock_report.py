from odoo import models, fields


class StockReport(models.Model):
    _inherit = "stock.report"

    brand_id = fields.Many2one("product.breeder", string="Brand")

    def _select(self):
        return super()._select() + ", t.product_breeder_id as brand_id"

    def _group_by(self):
        res = super()._group_by()
        res += ", t.product_breeder_id"
        return res
