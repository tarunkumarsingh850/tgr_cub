from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date
import ast
from odoo.tools import float_is_zero, float_compare


website_dict = {
    1 : 'tigerone_uk',
    2 : 'tigerone_eu',
    3 : 'tigerone_sa',
    4 : 'seedsman_uk',
    5 : 'seedsman_usa',
    6 : 'seedsman_eu',
    7 : 'seedsman_sa',
    8 : 'eztestkits_uk',
    9 : 'eztestkits_usa',
    10 : 'eztestkits_eu',
    11 : 'eztestkits_sa',
    12 : 'python',
    13 : 'tigerone_usa',
    14 : 'wholesale',
    15 : 'uk3pl',
    20 :'seedsman_usa',
}

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    order_type_id = fields.Many2one("sale.type", string="Order Type")
    is_hold = fields.Boolean("Hold", default=False, copy=False, tracking=True)
    hold_reason_id = fields.Many2one("hold.reason", string="Hold Reason", tracking=True)
    customer_order = fields.Char("Customer Order")
    requested_on = fields.Date("requested On", default=date.today())
    original_order = fields.Char("Original Order")
    delivery_status = fields.Selection(
        [
            ("no_delivery", "No Delivery"),
            ("draft", "Draft"),
            ("waiting", "Waiting Another Operation"),
            ("confirmed", "Waiting"),
            ("assigned", "Ready"),
            ("processing_batched", "Processing/Batched"),
            ("return", "Return"),
            ("done", "Shipped"),
            ("cancel", "Cancelled"),
        ],
        compute="_compute_delivery_status",
        store=True,
    )

    is_balance_to_deliver = fields.Boolean(
        string="Is Balance To Deliver", compute="_compute_balance_to_deliver", copy=False
    )
    shipment_tracking_reference = fields.Char("Shipment Tracking Reference", related="picking_ids.carrier_tracking_ref")
    order_hold_override_reason = fields.Text("Order Hold Override Reason", tracking=True)
    customer_class_tag = fields.Selection(
        [("wholesale", "Wholesale Customer"), ("retail", "Retail Customer")],
        compute="compute_customer_class",
        string="Customer Class",
    )
    credit_amount = fields.Float('Credit Amount', compute = 'compute_credit_amount')
    total_sale_credit_amount = fields.Float('Total Sale Credit Amount', compute = 'compute_credit_amount')
    websites = fields.Selection(
        [('magento', 'Magento Orders'),
         ('tigerone_uk','Tiger One UK'),
         ('tigerone_eu','Tiger One EU'),
         ('tigerone_sa','Tiger One SA'),
         ('seedsman_uk','Seedsman UK'),
         ('seedsman_usa','Seedsman USA'),
         ('seedsman_eu','Seedsman EU'),
         ('seedsman_sa','Seedsman SA'),
         ('eztestkits_uk',"Eztestkits UK"),
         ('eztestkits_usa',"Eztestkits USA"),
         ('eztestkits_eu',"Eztestkits EU"),
         ('eztestkits_sa',"Eztestkits SA"),
         ('python','Pytho N'),
         ('tigerone_usa','Tiger One USA'),
         ('wholesale','Wholesale'),
         ('uk3pl','UK3PL'),
        ('shopify', 'Shopify Orders'),
        ('barney', "Barney's Orders"),
        ('dropship', 'Dropshipping Orders'),
        ('dutch', "Dutch's Order"),
        ('direct','Direct Orders')], string="Websites", compute = '_compute_website_selection', store=True)

    @api.depends("order_line")
    def _compute_balance_to_deliver(self):
        is_balance_to_deliver = False
        for record in self:
            for line in record.order_line:
                if line.product_id.detailed_type == "product":
                    if line.product_qty > line.qty_delivered:
                        is_balance_to_deliver = True
                        break
            record.is_balance_to_deliver = is_balance_to_deliver

    def action_confirm(self):
        result = super(SaleOrderInherit, self).action_confirm()
        picking = self.picking_ids.filtered(lambda x: x.sale_id == self)
        if picking:
            reason = self.env["reason.code"].search([("name", "=", "Direct Issue")], limit=1)
            if reason:
                picking.reason_code_id = reason.id
            else:
                reason = self.env["ir.config_parameter"].sudo().get_param("bi_reason_code.sale_reason_id")
                if reason:
                    picking.reason_code_id = int(reason)
                else:
                    picking.reason_code_id = False
            for line in picking.move_ids_without_package:
                if line.sale_line_id:
                    line.sales_price = line.sale_line_id.price_subtotal
        return result

    def create_payment(self):
        journal_id = self.env["account.journal"].search([("type", "=", "bank")], limit=1)
        return {
            "name": _("payments"),
            "type": "ir.actions.act_window",
            "res_model": "account.payment",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_sale_id": self.id,
                "default_partner_id": self.partner_id.id,
                "default_amount": self.amount_total,
                "default_currency_id": self.currency_id.id,
                "default_journal_id": journal_id.id,
            },
        }

    def action_create_delivery_balance(self):
        self.order_line._action_launch_stock_rule()

    def action_update_stock_warehouse(self):
        return {
            "name": _("Switch Warehouse"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "sale.warehouse.update",
            "context": {
                "default_sale_ids": [(4, sale.id) for sale in self],
                "default_current_warehouse_ids": [(4, sale.warehouse_id.id) for sale in self],
            },
            "target": "new",
        }

    @api.depends("picking_ids", "picking_ids.state")
    def _compute_delivery_status(self):
        for rec in self:
            if rec.picking_ids:
                rec.delivery_status = rec.picking_ids[0].state
            else:
                rec.delivery_status = "no_delivery"

    def cancel_order_by_picking(self):
        for order in self:
            if all(picking.state == "cancel" for picking in order.picking_ids):
                order._action_cancel()

    def _compute_sold_qty(self):
        for rec in self.order_line:
            if rec.qty_delivered > 0:
                po_ids = (
                    self.env["purchase.order"]
                    .search(
                        [
                            ("is_consignment_used", "=", False),
                            ("is_consignment_order", "=", True),
                        ],
                        order="date_order ASC",
                    )
                    .filtered(
                        lambda po: any(
                            line.product_id == rec.product_id
                            and line.quantity_sold < line.qty_received
                            and line.warehouse_dest_id == rec.warehouse_id
                            for line in po.order_line
                        )
                    )
                )

                stop_iteration = False
                qty_left = rec.qty_delivered
                for po_id in po_ids:
                    if not stop_iteration:
                        for order_line in po_id.order_line:
                            if rec.product_id == order_line.product_id:
                                balance = qty_left + order_line.quantity_sold - order_line.qty_received
                                if balance > 0:
                                    order_line.quantity_sold += qty_left - balance
                                    rec.consignment_ids = [(4, po_id.id)]
                                    lines = [(0, 0, {"so_line_id": rec.id, "so_sold_qty": qty_left - balance})]
                                    so_id = po_id.write({"so_line_ids": lines})
                                    if so_id:
                                        rec.order_id.message_post(
                                            body=_(
                                                "{} Quantity of item {} moved from {} by {}".format(
                                                    qty_left - balance,
                                                    rec.product_id.name,
                                                    po_id.name,
                                                    self.env.user.name,
                                                )
                                            )
                                        )
                                    qty_left = balance
                                    break
                                elif balance <= 0:
                                    order_line.quantity_sold += qty_left
                                    rec.consignment_ids = [(4, po_id.id)]
                                    lines = [(0, 0, {"so_line_id": rec.id, "so_sold_qty": qty_left})]
                                    so_id = po_id.write({"so_line_ids": lines})
                                    if so_id:
                                        rec.order_id.message_post(
                                            body=_(
                                                "{} Quantity of item {} moved from {} by {}".format(
                                                    qty_left, rec.product_id.name, po_id.name, self.env.user.name
                                                )
                                            )
                                        )
                                    stop_iteration = True
                                    break

    def _prepare_confirmation_values(self):
        res = super(SaleOrderInherit, self)._prepare_confirmation_values()
        del res["date_order"]
        return res

    @api.model
    def create(self, vals):
        order = super(SaleOrderInherit, self).create(vals)
        if order.partner_id.user_id and order.partner_id.user_id != order.user_id:
            order.user_id = order.partner_id.user_id.id
        elif order.partner_id.user_id and order.partner_id.user_id == order.user_id:
            pass
        else:
            order.user_id = self.env.user.id
        if order.partner_id.is_credit_customer and order.partner_id.credit_verification == "abled":
            total = order.amount_total + order.partner_id.available_credit
            if order.partner_id.available_credit <= 0 or total > order.partner_id.credit_limit:
                hold_reason = self.env["hold.reason"].search([("is_credit_limit_exceeded", "=", True)])
                if not hold_reason:
                    raise UserError(_("Credit limit exceeded hold reason not found."))
                order.write({"is_hold": True, "hold_reason_id": hold_reason.id})
                notification_ids = [
                    (0, 0, {"res_partner_id": order.user_id.partner_id.id, "notification_type": "inbox"})
                ]
                self.env["mail.message"].create(
                    {
                        "message_type": "notification",
                        "body": _(f"Order {order.name} on hold due to exceeded credit limit."),
                        "subject": "Credit limit exceeded",
                        "partner_ids": [(4, order.user_id.partner_id.id)],
                        "model": order._name,
                        "res_id": order.id,
                        "notification_ids": notification_ids,
                        "author_id": self.env.user.partner_id and self.env.user.partner_id.id,
                    }
                )
        fraud_score_value = (
                self.env["ir.config_parameter"].sudo().get_param("bi_sale_generic_customisation.fraud_score")
            )
        if order.fraud_score and fraud_score_value and int(order.fraud_score) >= int(fraud_score_value):
            hold_reason = self.env["hold.reason"].search([("is_fraud_score", "=", True)],limit=1)
            order.write({"is_hold": True, "hold_reason_id": hold_reason and hold_reason.id or False})
        return order

    def hold_order(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Order Hold"),
            "res_model": "order.unhold.reason.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_order_id": self.id, "default_hold_type": "hold"},
        }

    def unhold_order(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Order Unhold"),
            "res_model": "order.unhold.reason.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_order_id": self.id, "default_hold_type": "unhold"},
        }

    @api.depends("partner_id")
    def compute_customer_class(self):
        for sale in self:
            sale.customer_class_tag = ""
            if sale.partner_id and sale.partner_id.customer_class_id:
                customer_class_id = sale.partner_id.customer_class_id
                if customer_class_id.is_wholesales:
                    sale.customer_class_tag = "wholesale"
                elif (
                    customer_class_id.is_dropshipping
                    or customer_class_id.is_barneys_customer
                    or customer_class_id.is_salesman
                    or customer_class_id.is_eztest
                    or customer_class_id.is_shopify
                ):
                    sale.customer_class_tag = "retail"


    def _action_margin_sale_order(self):
        for rec in self.order_line:
            rec.with_context(is_compute=True)._compute_purchase_price()

    @api.depends('invoice_ids')
    def compute_credit_amount(self):
        for rec in self:
            if rec.invoice_ids.filtered(lambda i: i.state == 'posted' and i.move_type == 'out_refund'):
                rec.credit_amount = sum(rec.invoice_ids.filtered(lambda i: i.state == 'posted' and i.move_type == 'out_refund').mapped('amount_total'))
            else:
                rec.credit_amount = 0.00
            rec.total_sale_credit_amount = rec.credit_amount and rec.amount_total - rec.credit_amount or 0.00

    @api.depends('magento_order_id','shopify_order_id','is_drop_shipping')
    def _compute_website_selection(self):
        for rec in self:
            rec.websites = False
            if rec.magento_order_id:
                website_id = self.env['magento.website'].search([('id','=', rec.magento_website_id.id)])
                if website_id:
                    rec.websites = website_dict[website_id.id]
                else:
                    rec.websites = 'magento'
            elif rec.shopify_order_id:
                rec.websites = 'shopify'
            elif rec.is_drop_shipping:
                rec.websites = 'dropship'
            else:
                rec.websites = 'direct'


class SaleLineInherit(models.Model):
    _inherit = "sale.order.line"

    discount_amount_line = fields.Float("Discount Amount")
    product_sku = fields.Char("SKU", related="product_id.default_code")

    @api.onchange("product_id")
    def _onchange_brand_product(self):
        result = self.env["ir.config_parameter"].sudo().get_param("bi_customer_generic_customization.company_res_ids")
        if result:
            company_ids = self.env["res.company"].search([("id", "in", ast.literal_eval(result))])
            for each in self:
                if each.product_id:
                    if each.order_id.company_id.id in company_ids.ids:
                        for line in each.order_id.partner_id.brand_product_ids:
                            if line.brand_id.id == each.product_id.product_tmpl_id.product_breeder_id.id:
                                self.write(
                                    {
                                        "discount": line.discount,
                                    }
                                )

    @api.onchange("discount_amount_line", "product_uom_qty", "price_unit")
    def _onchange_discount_amount(self):
        for each in self:
            each.discount = 0
            if each.discount_amount_line:
                dis_percent = each.product_uom_qty * each.price_unit and (each.discount_amount_line / (each.product_uom_qty * each.price_unit)) * 100 or 0.00
                each.discount = dis_percent

    @api.onchange("product_uom_qty", "price_unit", "discount")
    def _onchange_discount_amount_percentage(self):
        for each in self:
            if each.discount:
                dis_percent = (each.product_uom_qty * each.price_unit) * (each.discount / 100)
                each.discount_amount_line = dis_percent

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleLineInherit, self)._prepare_invoice_line(**optional_values)
        res["discount_amount"] = self.discount_amount_line
        return res


    @api.depends('product_id', 'company_id', 'currency_id', 'product_uom')
    def _compute_purchase_price(self):
        res = super(SaleLineInherit, self)._compute_purchase_price()
        if 'is_compute' in self._context:
            for line in self:
                if not line.product_id:
                    line.purchase_price = 0.0
                    continue
                line = line.with_company(line.company_id)
                product_cost = line.product_id.standard_price
                line.purchase_price = line._convert_price(product_cost, line.product_id.uom_id)
        return res
    


    @api.depends('state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice', 'qty_invoiced')
    def _compute_invoice_status(self):
        """
        Compute the invoice status of a SO line. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also hte default value if the conditions of no other status is met.
        - to invoice: we refer to the quantity to invoice of the line. Refer to method
          `_get_to_invoice_qty()` for more information on how this quantity is calculated.
        - upselling: this is possible only for a product invoiced on ordered quantities for which
          we delivered more than expected. The could arise if, for example, a project took more
          time than expected but we decided not to invoice the extra cost to the client. This
          occurs onyl in state 'sale', so that when a SO is set to done, the upselling opportunity
          is removed from the list.
        - invoiced: the quantity invoiced is larger or equal to the quantity ordered.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if line.state not in ('sale', 'done'):
                line.invoice_status = 'no'
            elif line.is_downpayment and line.untaxed_amount_to_invoice == 0:
                line.invoice_status = 'invoiced'
            # elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
            #     line.invoice_status = 'to invoice'
            # elif line.state == 'sale' and line.product_id.invoice_policy == 'order' and\
            #         line.product_uom_qty >= 0.0 and\
            #         float_compare(line.qty_delivered, line.product_uom_qty, precision_digits=precision) == 1:
            #     line.invoice_status = 'upselling'
            # elif float_compare(line.qty_invoiced, line.product_uom_qty, precision_digits=precision) >= 0:
            #     line.invoice_status = 'invoiced'
            elif line.order_id.invoice_ids:
                for inv in line.order_id.invoice_ids.filtered(lambda i : i.state != 'cancel' and i.move_type in ('out_invoice', 'out_refund')):
                    if inv.state == 'posted':
                        line.invoice_status = 'invoiced'
                    if inv.state == 'draft':
                        line.invoice_status = 'to invoice'
            else:
                line.invoice_status = 'no'

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        res = super(SaleLineInherit, self).product_uom_change()
        country_code = self.env.company.country_id.code
        if self.product_id:
            if country_code in ['GB', 'ES']:
                self.price_unit = self.product_id.product_tmpl_id.wholesale_price_value and self.product_id.product_tmpl_id.wholesale_price_value or 0.00
            if country_code == 'US':
                self.price_unit = self.product_id.product_tmpl_id.wholesale_us and self.product_id.product_tmpl_id.wholesale_us or 0.00
        return res