from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    shipping_company_name = fields.Char(
        string="Shipping Company Name",
    )
