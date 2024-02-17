from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    high_alert_customer = fields.Boolean(string="High Alert Customer", default=False)
    usa_charge_back = fields.Boolean(string="Charge Back Customer", default=False)
