from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    uk_street = fields.Char(string="Street")
    uk_street2 = fields.Char(string="Street2")
    uk_zip = fields.Char(string="Zip")
    uk_city = fields.Char(string="City")
    uk_state_id = fields.Many2one(
        "res.country.state", string="Fed. State", domain="[('country_id', '=?', uk_country_id)]"
    )
    uk_country_id = fields.Many2one("res.country", string="Country")
    uk_email = fields.Char(string="Email")
    uk_phone = fields.Char(string="Phone")
