from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = "product.category"

    taxjar_category_id = fields.Many2one("taxjar.category", "Taxjar Category")
