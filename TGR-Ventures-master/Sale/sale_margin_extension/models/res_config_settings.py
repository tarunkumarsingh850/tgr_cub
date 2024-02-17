from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_sale_margin_extension = fields.Boolean("Margins")
