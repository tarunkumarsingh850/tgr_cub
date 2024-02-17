from odoo import fields, models,api


class AccountsMoveLine(models.Model):
    _inherit = "account.move.line"

    product_sku = fields.Char("SKU", related="product_id.default_code")
    pack_size = fields.Char(string="Pack Size", related="product_id.product_tmpl_id.pack_size_desc")
    customer_class_id = fields.Many2one("customer.class",related='partner_id.customer_class_id', string="Customer Class", store=True)
    salesperson_partner_id = fields.Many2one("res.users",related='partner_id.user_id', string="Salesperson",store=True)

    # OVERRIDE THE FUNCTION TO CHANGE ACCOUNTS IN INVOICE
    def _get_computed_account(self):
        self.ensure_one()
        self = self.with_company(self.move_id.journal_id.company_id)

        if not self.product_id:
            return

        fiscal_position = self.move_id.fiscal_position_id
        if self.move_id.move_type in ("out_invoice", "out_refund"):
            if self.env.company.id == 10:
                if self.partner_id.sales_account_id:
                    account_id = self.partner_id.sales_account_id
                elif self.move_id.partner_id.sales_account_id:
                    account_id = self.move_id.partner_id.sales_account_id
                elif self.move_id.journal_id.default_account_id:
                    account_id = self.move_id.journal_id.default_account_id
                else:
                    accounts = self.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
            elif self.move_id.journal_id.default_account_id:
                account_id = self.move_id.journal_id.default_account_id
            else:
                accounts = self.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
        else:
            accounts = self.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
        if self.move_id.is_sale_document(include_receipts=True):
            # Out invoice.
            if account_id:
                return account_id
            else:
                return accounts["income"] or self.account_id
        elif self.move_id.is_purchase_document(include_receipts=True):
            # In invoice.
            return accounts["expense"] or self.account_id
        

    @api.onchange('product_uom_id')
    def _onchange_uom_id(self):
        res = super(AccountsMoveLine, self)._onchange_uom_id()
        country_code = self.env.company.country_id.code
        if self.move_id.move_type in ['out_invoice','out_refund']:
            if self.product_id:
                if country_code in ['GB', 'ES']:
                    self.price_unit = self.product_id.product_tmpl_id.wholesale_price_value and self.product_id.product_tmpl_id.wholesale_price_value or 0.00
                if country_code == 'US':
                    self.price_unit = self.product_id.product_tmpl_id.wholesale_us and self.product_id.product_tmpl_id.wholesale_us or 0.00
        return res
