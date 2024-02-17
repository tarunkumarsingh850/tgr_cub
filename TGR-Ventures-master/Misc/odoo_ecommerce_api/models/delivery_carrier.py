from odoo import models, fields


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"
    _description = "Delivery Carrier"

    is_dropshipping_delivery = fields.Boolean("Is Dropshipping Delivery", copy=False)
