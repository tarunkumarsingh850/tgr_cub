from odoo import models, fields


class HoldReason(models.Model):
    _name = "hold.reason"
    _description = "Hold Reason"

    name = fields.Char()
    is_credit_limit_exceeded = fields.Boolean("Is Credit Limit Exceeded")
    is_fraud_score = fields.Boolean("Is Fraud Score")
