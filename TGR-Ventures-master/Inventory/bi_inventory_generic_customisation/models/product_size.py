from odoo import fields, models


class ProductSize(models.Model):
    _name = "product.size"
    _rec_name = "product_size_des"

    product_size = fields.Char(string="Product Size")
    product_size_des = fields.Char(string="Product Size Description")
