from odoo import models, fields


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"
    _description = "Delivery Carrier"

    is_barneys_delivery = fields.Boolean("Is Barneys Delivery", copy=False)
