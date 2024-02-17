from odoo import fields, models


class SalesPersonLine(models.Model):
    _name = "sales.person.line"

    name = fields.Char(string="Name", required=True)
    user_id = fields.Many2one("res.users", string="Sales Person")
    commission_percentage = fields.Float(string="Commission (%)")
    partner_id = fields.Many2one("res.partner", string="Partner")
