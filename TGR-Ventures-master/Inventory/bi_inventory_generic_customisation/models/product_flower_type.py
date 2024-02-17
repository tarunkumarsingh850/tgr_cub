from odoo import fields, models


class ProductFlowerType(models.Model):
    _name = "flower.type"
    _rec_name = "flower_type_des"

    flower_type = fields.Char(string="Flower Type")
    flower_type_des = fields.Char(string="Flower Type Description")
    magento_id = fields.Char(
        string="Magento ID",
    )
