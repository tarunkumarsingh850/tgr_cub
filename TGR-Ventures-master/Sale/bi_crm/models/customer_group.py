from odoo import fields, models


class CustomerGroup(models.Model):
    _name = "customer.group"
    _description = "Customer Group"

    name = fields.Char("Name")
    code = fields.Char("Code")
