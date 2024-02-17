from odoo import fields, models, api, _
from odoo.exceptions import UserError


class CustomerMaster(models.Model):
    _name = "customer.class"

    name = fields.Char(string="Class Name", required=True)
    shortcode = fields.Char(string="Short Code", required=True)
    description = fields.Char(string="Descrpition")
    country_id = fields.Many2one("res.country", string="Country")
    payment_term_id = fields.Many2one("account.payment.term", string="Payment Terms")
    journal_id = fields.Many2one("account.journal", string="Payment Method", domain=[("type", "in", ("cash", "bank"))])
    company_id = fields.Many2one("res.company", string="Company")
    is_dropshipping = fields.Boolean(
        string="Is Drop Shipping",
    )
    is_wholesales = fields.Boolean(
        string="Is Wholesale",
    )
    is_salesman = fields.Boolean(
        string="Is Seedsman",
    )
    is_eztest = fields.Boolean(
        string="Is Eztest",
    )
    is_shopify = fields.Boolean(
        string="Is Shopify",
    )
    website_ids = fields.Many2many("magento.website", string="Website")
    receivable_account_code_prefix = fields.Char("Receivable Account Code Prefix", size=4)

    @api.onchange("is_dropshipping", "is_salesman", "is_wholesales")
    def _onchange_is_check(self):
        customer_class = self.env["customer.class"]
        if self.is_dropshipping == True:
            record = customer_class.search([("is_dropshipping", "=", True)])
            if record:
                raise UserError(_("Droshipping is already assigned"))
        if self.is_wholesales == True:
            record = customer_class.search([("id", "not in", self.ids), ("is_wholesales", "=", True)])
            if record:
                raise UserError(_("Wholesales is already assigned"))
        if self.is_salesman == True:
            record = customer_class.search([("is_salesman", "=", True)])
            if record:
                raise UserError(_("Seedsman is already assigned"))
        if self.is_eztest == True:
            record = customer_class.search([("is_eztest", "=", True)])
            if record:
                raise UserError(_("Eztest is already assigned"))
        if self.is_shopify == True:
            record = customer_class.search([("is_shopify", "=", True)])
            if record:
                raise UserError(_("Shopify is already assigned"))
