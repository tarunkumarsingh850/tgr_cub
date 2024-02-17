from odoo import fields, models


class ResCountry(models.Model):
    _inherit = "res.country"

    country_group_id = fields.Many2one(
        string="Country Group",
        comodel_name="res.country.group",
    )
