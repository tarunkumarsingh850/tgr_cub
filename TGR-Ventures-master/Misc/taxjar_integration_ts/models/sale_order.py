from odoo import fields, api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    ##Commented on date 21-Jan-2020 because we don't need to auto fill fiscal position
    @api.onchange("partner_shipping_id", "partner_id")
    def onchange_partner_shipping_id(self):
        """
        Trigger the change of fiscal position when the shipping address is modified.
        if no any fiscal position while creating order then check in which fiscal position in taxjar account if got multiple then select first one.
        """
        res = super(SaleOrder, self).onchange_partner_shipping_id()
        if self.fiscal_position_id:
            taxjar_acc_id = self.fiscal_position_id and self.fiscal_position_id.taxjar_account_id or False
            if taxjar_acc_id and taxjar_acc_id.state == "confirm":
                self.order_line._compute_tax_id_from_taxjar(taxjar_acc_id, self.partner_shipping_id)
        return res

    @api.onchange("fiscal_position_id")
    def _compute_tax_id(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the SO.
        """
        res = super(SaleOrder, self)._compute_tax_id()
        for order in self:
            taxjar_account_id = order.fiscal_position_id.taxjar_account_id
            if taxjar_account_id and taxjar_account_id.state == "confirm":
                order.order_line._compute_tax_id_from_taxjar(taxjar_account_id, order.partner_shipping_id)
        return res

    @api.onchange("warehouse_id")
    def _onchange_warehouse_id(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the SO.
        """
        # res = super(SaleOrder, self)._onchange_warehouse_id()
        for order in self:
            taxjar_account_id = order.fiscal_position_id.taxjar_account_id
            if taxjar_account_id and taxjar_account_id.state == "confirm":
                order.order_line._compute_tax_id_from_taxjar(taxjar_account_id, order.partner_shipping_id)
        # return res

    # @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed')
    # def _compute_tax_totals_json(self):
    #     def compute_taxes(order_line):
    #         price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
    #         order = order_line.order_id
    #         return order_line.tax_id._origin.compute_all(price, order.currency_id, order_line.product_uom_qty, product=order_line.product_id, partner=order.partner_shipping_id)
    #
    #     account_move = self.env['account.move']
    #     for order in self:
    #         tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line, compute_taxes)
    #         tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total, order.amount_untaxed, order.currency_id)
    #         groups_by_subtotal = tax_totals.get('groups_by_subtotal', {})
    #         for groups_by_subtotal in groups_by_subtotal.values():
    #             for group_tax in groups_by_subtotal:
    #                 group_tax.update({'tax_group_amount': round(order.amount_tax, 2)})
    #                 group_tax.update(({'formatted_tax_group_amount': formatLang(self.env, order.amount_tax, currency_obj=order.currency_id)}))
    #         order.tax_totals_json = json.dumps(tax_totals)

    def _create_delivery_line(self, carrier, price_unit):
        sol = super(SaleOrder, self)._create_delivery_line(carrier, price_unit)
        sol._compute_tax_id()
        return sol

    # def _create_invoices(self, grouped=False, final=False, date=None):
    #     moves = super(SaleOrder, self)._create_invoices(grouped=grouped,final=final,date=date)
    #     for move in moves:
    #         for line in move.invoice_line_ids:
    #             line.tax_base_amount = sum(line.sale_line_ids.mapped('price_tax'))
    #     return moves


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    decrease_taxamount = fields.Float(
        "Decrease Taxes",
        help="Decrease Taxes for some categories. Writen temp taxes on this field. Get exact Taxes per line for specific category product.",
    )
    tax_base_amount_ts = fields.Float(
        "TaxBaseAmount(TaxJar)",
        help="This field used when tax base amount less of actual subtotal. This field values come from TaxJar based on customer address and TaxJar product Category.",
    )

    def _prepare_invoice_line(self, **optional_values):
        ##modified for 'decrease_taxamount' field to manually applied taxes
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res["decrease_taxamount"] = self.decrease_taxamount
        res["tax_base_amount_ts"] = self.tax_base_amount_ts
        return res

    def get_taxjar_category(self):
        taxjar_category_id = self.product_id and self.product_id.taxjar_category_id or False
        if not taxjar_category_id:
            taxjar_category_id = (
                self.product_id and self.product_id.categ_id and self.product_id.categ_id.taxjar_category_id or False
            )
        return taxjar_category_id

    def _compute_tax_id(self):
        """Implement Taxjar Taxes while creating order line or any changes"""
        compute_taxes_line = self.filtered(
            lambda x: x.order_id.fiscal_position_id.taxjar_account_id.state == "confirm"
            or x.order_id.partner_id.property_account_position_id.taxjar_account_id.state == "confirm"
        )
        no_taxes_line = self - compute_taxes_line
        for line in compute_taxes_line:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            if fpos.taxjar_account_id and fpos.taxjar_account_id.state == "confirm":
                line._compute_tax_id_from_taxjar(fpos.taxjar_account_id, line.order_id.partner_shipping_id)
                # return True
        if no_taxes_line:
            return super(SaleOrderLine, no_taxes_line)._compute_tax_id()

    def _compute_tax_id_from_taxjar(self, taxjar_account_id, shipping_partner):
        for line in self:
            rec_partner = line.order_id.warehouse_id and line.order_id.warehouse_id.partner_id or False
            if line.price_unit and rec_partner:
                taxjar_category = line.get_taxjar_category() or self.env["taxjar.category"]
                product_tax_code = taxjar_category and taxjar_category.product_tax_code or ""
                shipping_charge = line.is_delivery and line.price_subtotal or 0.0
                discount_amount = (
                    line.discount and (line.product_uom_qty * line.price_unit) * line.discount / 100 or 0.0
                )
                line_dict = {
                    "amount": not shipping_charge and line.price_subtotal or 0.0,
                    "shipping": shipping_charge,
                    "line_items": [
                        {
                            "quantity": line.product_uom_qty,
                            "product_tax_code": product_tax_code,
                            "unit_price": not shipping_charge and line.price_unit or 0.0,
                            "discount": discount_amount,
                        }
                    ],
                }
                tax_id, tax_amount, taxable_amount = taxjar_account_id.get_taxes(
                    line_dict, taxjar_category, rec_partner, shipping_partner, line.is_delivery
                )
                line.tax_id = tax_id
                line.decrease_taxamount = tax_amount
                line.tax_base_amount_ts = taxable_amount

    # added: added a code from supper called deafult onchanged to this custom, as tax_id field was not editable
    @api.onchange(
        "price_unit",
        "discount",
        "product_uom_qty",
    )
    def _onchange_discount_custom(self):
        for line in self:
            line._compute_tax_id()
            if line.decrease_taxamount:
                line.update(
                    {
                        "price_tax": line.decrease_taxamount,
                    }
                )

    # @api.onchange('price_unit')
    # def price_unit_change(self):
    #     order_id = self.order_id
    #     if order_id:
    #         taxjar_account_id = order_id.fiscal_position_id.taxjar_account_id
    #         if order_id.warehouse_id and taxjar_account_id and taxjar_account_id.state == 'confirm':
    #             self._compute_tax_id_from_taxjar(taxjar_account_id, order_id.partner_shipping_id)
