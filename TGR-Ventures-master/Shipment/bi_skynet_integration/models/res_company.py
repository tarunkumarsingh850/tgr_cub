from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"
    _description = "Res Company"

    skynet_api_url = fields.Char("Skynet API URL")
