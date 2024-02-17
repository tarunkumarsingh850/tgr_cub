from odoo import fields, models


class StockValuation(models.Model):
    _inherit = "stock.valuation.layer"

    brand_id = fields.Many2one(
        "product.breeder", string="Brand", related="product_id.product_tmpl_id.product_breeder_id"
    )
    unit_cost = fields.Monetary("Unit Value", readonly=True, group_operator="avg")
