from odoo import models, fields


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"
    _description = "Delivery Carrier"

    is_dutch_delivery = fields.Boolean("Is Dutch Delivery", copy=False)
