from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Added for 'decrease_taxamount' field to manually applied taxes
    decrease_taxamount = fields.Float(
        "Decrease Taxes", help="Decrease Taxes for some categories. Writen temp taxes on this field."
    )
    tax_base_amount_ts = fields.Float(
        "TaxBaseAmount(TaxJar)",
        help="This field used when tax base amount less of actual subtotal. This field values come from TaxJar based on customer address and TaxJar product Category.",
    )

    def convert_amount_in_usd(self, amount):
        usd_currency = self.env.ref("base.USD")
        date = self.move_id.date or self.move_id.date_invoice
        return self.currency_id._convert(amount, usd_currency, self.company_id, date)

    def get_taxjar_category(self):
        "Find categories for taxjar"
        taxjar_category_id = self.product_id and self.product_id.taxjar_category_id or False
        if not taxjar_category_id:
            taxjar_category_id = (
                self.product_id and self.product_id.categ_id and self.product_id.categ_id.taxjar_category_id or False
            )
        return taxjar_category_id

    @api.onchange("account_id")
    def _onchange_account_id(self):
        "Need to empty invoice line taxes when fiscal position with taxjar confirmed account"
        if not self.account_id:
            return
        if (
            self.move_id.fiscal_position_id
            and self.move_id.fiscal_position_id.taxjar_account_id
            and self.move_id.fiscal_position_id.taxjar_account_id.state == "confirm"
        ):
            self.tax_ids = False
        else:
            super(AccountMoveLine, self)._onchange_account_id()

    # added: added a code from supper called deafult onchanged to this custom, as tax_id field was not editable
    @api.onchange("quantity", "discount", "price_unit")
    def _onchange_price_subtotal_custom(self):
        for line in self.filtered(
            lambda x: x.sale_line_ids.filtered(lambda x: not x.is_downpayment and not x.is_delivery)
            or not x.sale_line_ids
        ):
            line._get_computed_taxes()

    # def _set_price_and_tax_after_fpos(self):
    #     super(AccountMoveLine, self)._set_price_and_tax_after_fpos()
    #     if self.move_id and self.move_id.move_type in ('out_invoice', 'out_refund'):
    #         fpos = self.move_id.fiscal_position_id or False
    #         if fpos and fpos.taxjar_account_id and fpos.taxjar_account_id.state == 'confirm':
    #             self._compute_inv_line_tax_id_from_taxjar(fpos.taxjar_account_id, self.move_id.partner_shipping_id)

    def _get_computed_taxes(self):
        self.ensure_one()
        res = super(AccountMoveLine, self)._get_computed_taxes()
        fpos = self.move_id.fiscal_position_id or False
        taxjar_account_id = fpos and fpos.taxjar_account_id or False
        partner_id = self.move_id.partner_id or False
        if (
            taxjar_account_id
            and partner_id
            and partner_id.state_id
            and partner_id.state_id in taxjar_account_id.state_ids
        ):
            if (
                self.move_id
                and self.move_id.move_type in ("out_invoice", "out_refund")
                and self.product_id
                and fpos
                and fpos.taxjar_account_id
                and fpos.taxjar_account_id.state == "confirm"
            ):
                self._compute_inv_line_tax_id_from_taxjar(fpos.taxjar_account_id, self.move_id.partner_shipping_id)
                res = self.tax_ids
        return res

    def _compute_inv_line_tax_id_from_taxjar(self, taxjar_account_id, shipping_partner):
        "Compute Invoices Line taxes"
        for rec in self:
            rec_partner = rec.move_id.company_id and rec.move_id.company_id.partner_id or False
            if rec.price_unit and rec_partner:
                taxjar_category = rec.get_taxjar_category() or self.env["taxjar.category"]
                product_tax_code = taxjar_category and taxjar_category.product_tax_code or ""
                shipping_charge = 0.0  ##in the invoice line product we only able to select salling product(sale_ok).
                discount_amount = rec.discount and (rec.quantity * rec.price_unit) * rec.discount / 100 or 0.0
                line_dict = {
                    "amount": rec.price_subtotal or 0.0,
                    "shipping": shipping_charge,
                    "line_items": [
                        {
                            "quantity": rec.quantity,
                            "product_tax_code": product_tax_code,
                            "unit_price": rec.price_unit,
                            "discount": discount_amount,
                        }
                    ],
                }
                # is_delivery is False because we can't able to select thoes type of product in the invoice line
                tax_ids, tax_amount, taxable_amount = taxjar_account_id.get_taxes(
                    line_dict, taxjar_category, rec_partner, shipping_partner, False
                )
                rec.tax_ids = tax_ids
                rec.tax_base_amount_ts = taxable_amount
                rec.decrease_taxamount = tax_amount
