from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "stock.warehouse"

    is_spain = fields.Boolean("Is Spain")
    is_uk = fields.Boolean("Is UK")
    is_credit_note_email = fields.Boolean(
        string="Is Credit note Email",
        default=False,
        copy=False,
        help="If check-box is checked, when user create a credit note " "for particular warehouse email trigger.",
    )
