from odoo import fields, models


class ResCompanyMBE(models.Model):
    _inherit = "res.company"

    mbe_api_username = fields.Char(string="MBE Username")
    mbe_api_password = fields.Char(string="MBE Password")
