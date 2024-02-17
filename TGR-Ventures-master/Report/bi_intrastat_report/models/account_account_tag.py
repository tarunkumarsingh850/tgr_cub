from odoo import fields, models


class AccountAccountTag(models.Model):
    _inherit = "account.account.tag"

    is_intrastat = fields.Boolean(string="Is Intrastat")
