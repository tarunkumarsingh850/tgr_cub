from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountTax(models.Model):
    _inherit = "account.tax"

    code = fields.Char(
        string="Code",
    )

    is_export_tax = fields.Boolean("Is Exportation", default=False)
    is_intra_operation = fields.Boolean("Is Intracommunity Operation", default=False)

    @api.constrains("code")
    def _constrains_code(self):
        for rec in self:
            is_exists = self.env["account.tax"].search(
                [
                    ("id", "!=", rec.id),
                    ("code", "=", rec.code),
                ]
            )
            if is_exists:
                raise UserError(_(f" {rec.code} already exists."))
