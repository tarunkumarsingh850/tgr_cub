from odoo import models, fields


class PaymentMethodCode(models.Model):
    _name = "payment.method.code"
    _description = "Payment Method Code"

    payment_code = fields.Char("Payment Code")
    workflow_id = fields.Many2one("sale.workflow.process.ept", string="workflow")
    company_id = fields.Many2one("res.company", string="Company")
