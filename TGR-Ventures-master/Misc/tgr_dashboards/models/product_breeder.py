from odoo import fields, models


class ProductBreeder(models.Model):
    _inherit = "product.breeder"

    dashboard_rgb_color_code = fields.Char("Dashboard RGB Color Code", default="rgb(255, 102, 204)")
    is_visible_in_dashboard = fields.Boolean(
        "Is Visible In Dashboard", help="Enabling this option will show products in this breed as a " "separate breed"
    )
