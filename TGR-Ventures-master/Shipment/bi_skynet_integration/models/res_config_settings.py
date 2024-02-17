from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    _description = "Res Config Settings"

    skynet_api_url = fields.Char("Skynet API URL", related="company_id.skynet_api_url", readonly=False)
