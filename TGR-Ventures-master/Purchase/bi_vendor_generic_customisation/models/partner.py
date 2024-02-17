from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    vendor_class_id = fields.Many2one("vendor.class", string="Vendor Class")
    vendor_code = fields.Char(string="Vendor ID")
    # Accounts
    exp_account_id = fields.Many2one("account.account", string="Expense Acc.", company_dependent=True)
    disc_account_id = fields.Many2one("account.account", string="Discount Acc.", company_dependent=True)
    cash_account_id = fields.Many2one("account.account", string="Cash Discount Acc.", company_dependent=True)
    pre_account_id = fields.Many2one("account.account", string="Prepayment Acc.", company_dependent=True)
    po_account_id = fields.Many2one("account.account", string="PO Accrual Acc.", company_dependent=True)
    sales_account_id = fields.Many2one("account.account", string="Sales Acc.", company_dependent=True)
    freight_account_id = fields.Many2one("account.account", string="Freight Account", company_dependent=True)
    cash_account_vendor_id = fields.Many2one("account.account", string="Cash Account", company_dependent=True)
    # Analytic Accounts
    ap_sub_account_id = fields.Many2one("account.analytic.account", string="AP Sub Acc.", company_dependent=True)
    exp_sub_account_id = fields.Many2one("account.analytic.account", string="Exp Sub Acc.", company_dependent=True)
    disc_sub_account_id = fields.Many2one("account.analytic.account", string="Disc Sub Acc.", company_dependent=True)
    cash_sub_account_id = fields.Many2one(
        "account.analytic.account", string="Cash Disc Sub Acc.", company_dependent=True
    )
    pre_sub_account_id = fields.Many2one(
        "account.analytic.account", string="Prepayment Sub Acc.", company_dependent=True
    )
    po_sub_account_id = fields.Many2one(
        "account.analytic.account", string="PO Accrual Sub Acc.", company_dependent=True
    )
    sales_sub_account_id = fields.Many2one("account.analytic.account", string="Sales Sub Acc.", company_dependent=True)
    freight_sub_account_id = fields.Many2one(
        "account.analytic.account", string="Freight Sub Acc.", company_dependent=True
    )
    lead_days = fields.Integer("Lead Days", copy=False)
    taxes_ids = fields.Many2many("account.tax", "account_tax_ids__rel", string="Taxes")
    brand_ids = fields.Many2many("product.breeder", string="Brand")
    vendor_status = fields.Char(string="Acumatica Status")
    vendor_attention = fields.Char(string="Attention")
    vendor_external_id = fields.Char(string="Vendor External ID")
    vendor_rate_type = fields.Char(string="Curr. Rate Type")
    vendor_payment_method = fields.Char(string="Payment Method")
    vendor_payment_by = fields.Char(string="Payment By")
    vendor_warehouse = fields.Char(string="Warehouse")
    vendor_delivery_estimate = fields.Char(string="Delivery Estimate")
    vendor_discount_comment = fields.Char(string="Discount - Comments")
    vendor_ordering_method = fields.Char(string="Ordering Method")
    vendor_password = fields.Char(string="Password")
    vendor_username = fields.Char(string="Username")
    tax_zone = fields.Char(string="Tax Zone")
    product_type_id = fields.Many2one("vendor.product.type", string="Product Type")

    @api.constrains("vat", "country_id")
    def check_vat(self):
        # # The context key 'no_vat_validation' allows you to store/set a VAT number without doing validations.
        # # This is for API pushes from external platforms where you have no control over VAT numbers.
        # if self.env.context.get('no_vat_validation'):
        #     return

        # for partner in self:
        #     country = partner.commercial_partner_id.country_id
        #     if partner.vat and self._run_vat_test(partner.vat, country, partner.is_company) is False:
        #         partner_label = _("partner [%s]", partner.name)
        #         msg = partner._build_vat_error_message(country and country.code.lower() or None,
        #          partner.vat, partner_label)
        #         raise ValidationError(msg)
        pass

    @api.onchange("taxes_ids")
    def onchange_taxes_ids(self):
        if self.is_supplier:
            to_sync_companies = self.env["res.company"].search(
                [("synchronize_vendor_taxes", "=", True), ("id", "!=", self.env.company.id)]
            )
            if self.taxes_ids:
                taxes = self.taxes_ids.ids
                current_changed_taxes = self.env["account.tax"].browse(taxes)
                current_changed_taxes_names = current_changed_taxes.mapped("name")
                if len(current_changed_taxes_names) == 1:
                    domain = f"""name = '{current_changed_taxes_names[0]}'"""
                else:
                    domain = f"""name in {tuple(current_changed_taxes_names)}"""
                for sync_company in to_sync_companies:
                    query = f"""SELECT id FROM account_tax WHERE company_id={sync_company.id} AND {domain} AND type_tax_use='purchase'"""
                    self.env.cr.execute(query)
                    query_result = self.env.cr.dictfetchall()
                    taxes += [item["id"] for item in query_result]
                partner_id = self._origin.id
                remove_query = f"""DELETE FROM account_tax_ids__rel WHERE res_partner_id={partner_id}"""
                self.env.cr.execute(remove_query)
                for tax in taxes:
                    update_query = f"""INSERT INTO account_tax_ids__rel (res_partner_id, account_tax_id) VALUES ({partner_id}, {tax})"""
                    self.env.cr.execute(update_query)
            else:
                partner_id = self._origin.id
                remove_query = f"""DELETE FROM account_tax_ids__rel WHERE res_partner_id={partner_id}"""
                self.env.cr.execute(remove_query)
