from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_payment_posted = fields.Boolean("Is Payment Posted", default=False)
