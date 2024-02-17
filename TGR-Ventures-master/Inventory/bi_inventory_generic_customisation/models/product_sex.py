from odoo import fields, models


class ProductSex(models.Model):
    _name = "product.sex"
    _rec_name = "product_sex_des"

    product_sex = fields.Char(string="Product Sex")
    product_sex_des = fields.Char(string="Product Sex Description")
    magento_id = fields.Char(
        string="Magento ID",
    )
