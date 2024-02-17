from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    is_intrastat = fields.Boolean(string="Is Intrastat")
