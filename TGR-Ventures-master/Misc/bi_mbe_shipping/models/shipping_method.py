from odoo import fields, models


class ShippingMBE(models.Model):
    _inherit = "delivery.carrier"

    is_mbe = fields.Boolean("Is MBE")
