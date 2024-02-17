from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    description = fields.Char(string="Category Description")
    magento_id = fields.Char(
        string="Magento ID",
    )
    set_id = fields.Char("Set ID", copy=False)
