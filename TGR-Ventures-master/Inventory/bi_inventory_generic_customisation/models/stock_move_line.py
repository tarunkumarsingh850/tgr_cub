from odoo import fields, models


class StockMoveLineReport(models.Model):
    _inherit = "stock.move.line"

    brand_id = fields.Many2one(
        "product.breeder", string="Brand", related="product_id.product_tmpl_id.product_breeder_id", store=True
    )
    custom_origin = fields.Char(related="move_id.origin", string="Source", store=True)
    product_sku = fields.Char("SKU", related="product_id.default_code")
