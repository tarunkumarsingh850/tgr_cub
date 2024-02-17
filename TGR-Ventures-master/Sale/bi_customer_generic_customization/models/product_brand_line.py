from odoo import fields, models


class ProductBrndLine(models.Model):
    _name = "product.brand.line"

    discount = fields.Float(string="Discount")
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner")
    brand_id = fields.Many2one("product.breeder", string="Brand")
