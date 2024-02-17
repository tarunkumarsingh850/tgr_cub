from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    custom_country_id = fields.Many2one(
        string="Country Master",
        comodel_name="res.country",
    )
