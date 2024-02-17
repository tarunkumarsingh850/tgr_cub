from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    breed_available_in_dashboard = fields.Boolean(related="product_breeder_id.is_visible_in_dashboard", store=True)
