from odoo import models, fields


class PaymentMethodCode(models.Model):
    _inherit = "payment.method.code"

    payment_charge = fields.Float(string="Payment Charge", copy=False)
