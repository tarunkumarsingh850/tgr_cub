from odoo import models, fields


class AccountTax(models.Model):
    _inherit = "account.tax"

    is_uk_tax = fields.Boolean(
        string="Is UK Tax",
    )
