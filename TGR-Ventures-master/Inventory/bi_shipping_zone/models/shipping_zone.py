from odoo import fields, models


class ShippingZone(models.Model):
    _name = "shipping.zone"
    _description = "Shipping Zone Master"

    name = fields.Char()
