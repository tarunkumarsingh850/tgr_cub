from odoo import fields, models


class ShippingMethod(models.Model):
    _inherit = "delivery.carrier"

    is_express = fields.Boolean(string="Is Express", default=False, copy=False)
