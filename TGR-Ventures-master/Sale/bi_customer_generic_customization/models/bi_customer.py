from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_class_id = fields.Many2one("customer.class", string="Customer Class")
    customer_code = fields.Char(string="Customer Code")
    is_credit_customer = fields.Boolean(
        string="Is Credit Customer",
    )
    credit_verification = fields.Selection(
        [("abled", "Abled"), ("disabled", "Disabled")], string="Credit Verification", default="disabled"
    )
    credit_limit = fields.Float("Credit Limit", copy=False)
    credit_days_past_due = fields.Float("Credit Days Past Due", copy=False)
    unreleased_balance = fields.Float("Unreleased Balance", copy=False)
    open_ordered_balance = fields.Float("Open Ordered Balance", copy=False, compute="compute_open_ordered_balance")
    available_credit = fields.Float("Available Credit", copy=False, compute="compute_available_credit")
    first_due_date = fields.Date("First Due Date", copy=False)
    sales_person_line_ids = fields.One2many("sales.person.line", "partner_id", string="Sales Person")
    first_name = fields.Char(string="Name")
    last_name = fields.Char()
    customer_attention = fields.Char(string="Attention")
    customer_job_title = fields.Char(string="Job Title")
    customer_email = fields.Char(string="Email")
    account_address = fields.Char("Address Line 1")
    account_address_two = fields.Char("Address Line 2")
    contact_city = fields.Char("City")
    contact_state_id = fields.Many2one("res.country.state")
    contact_country_id = fields.Many2one("res.country")
    payment_journal_id = fields.Many2many("account.journal", string="Payment Method")
    # product_brand_ids = fields.One2many("product.brand.line", "partner_brand_id", string="Product Brand")
    brand_product_ids = fields.One2many(
        string="Product Brand",
        comodel_name="product.brand.line",
        inverse_name="partner_id",
    )
    payment_surcharge = fields.Float(
        string="Payment Surcharge",
    )
    picking_packing_cost = fields.Float(string="Picking and Packing Cost")
    invoice_company_name = fields.Char(string="Invoice Company Name")

    @api.onchange("contact_state_id")
    def _onchange_contact_state_id(self):
        for order in self:
            if order.contact_state_id:
                order.contact_country_id = order.contact_state_id.country_id.id

    def compute_open_ordered_balance(self):
        open_ordered_balance = 0
        if self.credit_verification == "abled":
            open_ordered_balance = self.debit - self.credit
            self.open_ordered_balance = abs(open_ordered_balance)
        else:
            self.open_ordered_balance = 0

    def compute_available_credit(self):
        self.available_credit = self.credit_limit - self.open_ordered_balance
