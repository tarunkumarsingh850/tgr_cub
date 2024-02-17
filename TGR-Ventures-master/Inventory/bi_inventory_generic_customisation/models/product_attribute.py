from odoo import fields, models


class ProductAttributeModel(models.Model):
    _name = "product.attribute.model"

    name = fields.Char("Attributes")
    stockout_boolean = fields.Boolean(string="Stock Out of date")
