from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    dashboard_chart_rgb_color = fields.Char("Dashboard Chart RGB Color Code", default="rgb(255, 170, 128)")
