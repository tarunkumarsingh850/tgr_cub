from odoo import fields, models


class PartnerCategory(models.Model):
    _name = "partner.category"

    name = fields.Char(string="Category")
