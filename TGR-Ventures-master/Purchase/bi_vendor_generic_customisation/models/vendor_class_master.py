from odoo import fields, models


class VendorClassMaster(models.Model):
    _name = "vendor.class"

    name = fields.Char(string="Class Name", required=True)
    description = fields.Char(string="Descrpition")
    country_id = fields.Many2one("res.country", string="Country")
    payment_term_id = fields.Many2one("account.payment.term", string="Payment Terms")
    journal_id = fields.Many2one("account.journal", string="Payment Method", domain=[("type", "in", ("cash", "bank"))])
    company_id = fields.Many2one("res.company", string="Company")
