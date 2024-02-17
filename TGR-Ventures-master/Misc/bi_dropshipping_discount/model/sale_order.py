import json

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    global_discount = fields.Float("Global Discount", default=0.0, copy=False)
    untaxed_amount_before_discount = fields.Monetary(
        "Untaxed Amount without Discount", compute="_amount_all",copy=False
    )
    global_discount_amount = fields.Monetary("Global Discount",compute="_amount_all", copy=False)

    @api.depends("order_line.price_total", "global_discount")
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            untaxed_amount_before_discount = amount_untaxed
            global_discount_amount = 0
            if order.global_discount > 0:
                global_discount_amount = round(
                    (untaxed_amount_before_discount * (order.global_discount / 100)), order.currency_id.decimal_places
                )
            amount_untaxed -= global_discount_amount
            order.update(
                {
                    "untaxed_amount_before_discount": untaxed_amount_before_discount,
                    "global_discount_amount": global_discount_amount,
                    "amount_untaxed": amount_untaxed,
                    "amount_tax": amount_tax,
                    "amount_total": amount_untaxed + amount_tax,
                }
            )

    @api.depends(
        "order_line.tax_id",
        "order_line.price_unit",
        "amount_total",
        "amount_untaxed",
        "global_discount",
        "untaxed_amount_before_discount",
        "global_discount_amount",
    )
    def _compute_tax_totals_json(self):
        def compute_taxes(order_line):
            price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
            order = order_line.order_id
            return order_line.tax_id._origin.compute_all(
                price,
                order.currency_id,
                order_line.product_uom_qty,
                product=order_line.product_id,
                partner=order.partner_shipping_id,
            )

        account_move = self.env["account.move"]
        for order in self:
            tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(
                order.order_line, compute_taxes
            )
            tax_totals = account_move._get_tax_totals(
                order.partner_id,
                tax_lines_data,
                order.amount_total,
                order.amount_untaxed,
                order.currency_id,
                order.untaxed_amount_before_discount,
                order.global_discount_amount,
            )
            order.tax_totals_json = json.dumps(tax_totals)

    def _prepare_sale_order_data(self, so_data, so_creation_type):
        res = super(SaleOrder, self)._prepare_sale_order_data(so_data, so_creation_type)
        if "error" not in res:
            order_index = -1
            for order in res:
                order_index += 1
                product_count = 0
                partner_id = order.get("partner_id")
                partner = self.env["res.partner"].browse(partner_id)
                order_line_index = -1
                for line in order.get("order_line"):
                    order_line_index += 1
                    product_id = line[2].get("product_id")
                    product_uom_qty = float(line[2].get("product_uom_qty"))
                    price_unit = float(line[2].get("price_unit"))
                    product = self.env["product.product"].browse(product_id)
                    if product.detailed_type == "product":
                        product_count += 1
                    discount = 0
                    discount_amount = 0
                    discount_line = False
                    for dline in partner.discount_line_ids:
                        if product.product_tmpl_id in dline.product_ids:
                            discount_line = dline
                            break
                    if not discount_line:
                        for dline in partner.discount_line_ids:
                            if product.product_tmpl_id.product_breeder_id in dline.brand_ids:
                                discount_line = dline
                                break
                    if discount_line:
                        discount = discount_line[0].percentage
                        discount_amount = (product_uom_qty * price_unit) * (discount / 100)
                    res[order_index]["order_line"][order_line_index][2].update(
                        {"discount": discount, "discount_amount_line": discount_amount}
                    )
                global_discount = 0
                if product_count <= 25:
                    order_sku_count = "25"
                elif product_count <= 50:
                    order_sku_count = "50"
                elif product_count <= 75:
                    order_sku_count = "75"
                elif product_count <= 100:
                    order_sku_count = "100"
                elif product_count > 100:
                    order_sku_count = "100+"
                global_discount_line = partner.global_discount_line_ids.filtered(
                    lambda gdisc: gdisc.order_sku_count == order_sku_count
                )
                if global_discount_line:
                    global_discount = global_discount_line.percentage
                res[order_index].update({"global_discount": global_discount})
        return res
