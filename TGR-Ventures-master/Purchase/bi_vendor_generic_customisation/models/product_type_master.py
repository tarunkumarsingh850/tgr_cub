from odoo import fields, models


class VendorProductType(models.Model):
    _name = "vendor.product.type"

    name = fields.Char(string="Product Type Name", required=True)
