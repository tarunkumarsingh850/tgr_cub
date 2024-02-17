from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    phytonation_chart_color_code = fields.Char("Dashboard Phytonation Chart RGB Color Code", default="rgb(0, 0, 0)")
    # customer_class_id = fields.Many2one("customer.class", string="Customer Class", required=True)
