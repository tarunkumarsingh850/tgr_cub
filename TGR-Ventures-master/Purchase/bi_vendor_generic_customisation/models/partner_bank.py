from odoo import fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    iban_number = fields.Char(string="IBAN Number")
