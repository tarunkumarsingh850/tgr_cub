# See LICENSE file for full copyright and licensing details.
"""
Describes fields and methods for create/ update sale order
"""
import pytz
from odoo import _, fields, models, api
from odoo.exceptions import UserError
from .api_request import req

utc = pytz.utc

MAGENTO_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SALE_ORDER_LINE = "sale.order.line"


class SaleOrder(models.Model):
    """
    Describes fields and methods for create/ update sale order
    """

    _inherit = "sale.order"

    fraud_score = fields.Char('Fraud Score')

    def _get_magento_order_status(self):
        """
        Compute updated_in_magento of order from the pickings.
        """
        for order in self:
            if order.magento_instance_id:
                pickings = order.picking_ids.filtered(lambda x: x.state != "cancel")
                stock_moves = order.order_line.move_ids.filtered(lambda x: not x.picking_id and x.state == "done")
                if pickings:
                    outgoing_picking = pickings.filtered(lambda x: x.location_dest_id.usage == "customer")
                    if all(outgoing_picking.mapped("is_exported_to_magento")):
                        order.updated_in_magento = True
                        continue
                if stock_moves:
                    order.updated_in_magento = True
                    continue
                order.updated_in_magento = False
                continue
            order.updated_in_magento = False

    def _search_magento_order_ids(self, operator, value):
        query = (
            """select so.id from stock_picking sp
                    inner join sale_order so on so.procurement_group_id=sp.group_id
                    inner join stock_location on stock_location.id=sp.location_dest_id and stock_location.usage='customer'
                    where sp.is_exported_to_magento %s true and sp.state != 'cancel'
                    """
            % operator
        )
        if operator == "=":
            query += """union all
                    select so.id from sale_order as so
                    inner join sale_order_line as sl on sl.order_id = so.id
                    inner join stock_move as sm on sm.sale_line_id = sl.id
                    where sm.picking_id is NULL and sm.state = 'done' and so.magento_instance_id notnull"""
        self._cr.execute(query)
        results = self._cr.fetchall()
        order_ids = []
        for result_tuple in results:
            order_ids.append(result_tuple[0])
        order_ids = list(set(order_ids))
        return [("id", "in", order_ids)]

    magento_instance_id = fields.Many2one(
        "magento.instance", string="Instance", help="This field relocates Magento Instance"
    )
    magento_order_id = fields.Char(string="Magento order Ids", help="Magento Order Id")
    magento_website_id = fields.Many2one("magento.website", string="Magento Website", help="Magento Website")
    magento_order_reference = fields.Char(string="Magento Orders Reference", help="Magento Order Reference")
    store_id = fields.Many2one("magento.storeview", string="Magento Storeview", help="Magento_store_view")
    is_exported_to_magento_shipment_status = fields.Boolean(
        string="Is Order exported to Shipment Status", help="Is exported to Shipment Status"
    )
    magento_payment_method_id = fields.Many2one(
        "magento.payment.method", string="Magento Payment Method", help="Magento Payment Method"
    )
    magento_payment_code = fields.Char("Magento Payment Code")
    magento_shipping_method_id = fields.Many2one(
        "magento.delivery.carrier", string="Magento Shipping Method", help="Magento Shipping Method"
    )
    order_transaction_id = fields.Char(string="Magento Orders Transaction ID", help="Magento Orders Transaction ID")
    updated_in_magento = fields.Boolean(
        string="Order fulfilled in magento",
        compute="_get_magento_order_status",
        search="_search_magento_order_ids",
        copy=False,
    )
    pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Pricelist",
        check_company=True,  # Unrequired company
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.",
    )
    cancel_reason = fields.Char("Reason for Cancel")
    is_cancel_reason = fields.Boolean("Reason for Cancel", default=False, copy=False)
    magento_status = fields.Char(
        string="Magento Status",
    )
    magento_billing_address = fields.Text(
        string="Magento Billing Address",
    )

    is_resend_order = fields.Boolean(
        string="Resend Order",
    )
    resend_reason = fields.Char("Resend Reason")

    _sql_constraints = [
        (
            "_magento_sale_order_unique_constraint",
            "unique(magento_order_id,magento_instance_id,magento_order_reference)",
            "Magento order must be unique",
        )
    ]

    def _cancel_order_exportable(self):
        """
        this method will check order is cancel in odoo or not, and invoice is exported or not.
        And shipment done in magento or not
        :return:
        """
        if (self.invoice_ids and True in self.invoice_ids.mapped("is_exported_to_magento")) or (
            self.picking_ids and self.picking_ids.filtered(lambda x: x.state == "done" and x.is_exported_to_magento).ids
        ):
            self.is_cancel_order_exportable = True
        else:
            self.is_cancel_order_exportable = False

    is_cancel_order_exportable = fields.Boolean(
        string="Is Invoice exportable", compute="_cancel_order_exportable", store=False
    )
    payment_id = fields.Many2one("account.payment", string="Payment", copy=False)
    payment_count = fields.Integer(string="Payment Count", compute="_compute_count_ids")

    @api.depends("payment_id")
    def _compute_count_ids(self):
        for order in self:
            order.payment_count = self.env["account.payment"].search_count([("sale_id", "=", self.id)])

    def action_view_payment(self):
        for order in self:
            payment_ids = self.env["account.payment"].search([("sale_id", "=", order.id)]).ids
            return {
                "name": "Account Payment",
                "type": "ir.actions.act_window",
                "view_mode": "tree,form",
                "res_model": "account.payment",
                "domain": [("id", "in", payment_ids)],
                "target": "current",
            }

    def create_sale_order_ept(self, item, instance, log, line_id):
        is_processed = self._find_price_list(item, log, line_id)
        order_line = self.env["sale.order.line"]
        if is_processed:
            customers = self.__update_partner_dict(item, instance)
            if 'firstname' in customers and customers['firstname'] == None:
                self.env["magento.order.data.queue.line.ept"].browse(line_id).state = 'failed'
                is_processed = False
            else:
                data = self.env["magento.res.partner.ept"].create_magento_customer(customers, True)
                item.update(data)
                is_processed = self.__find_order_warehouse(item, log, line_id)
                if is_processed:
                    is_processed = order_line.find_order_item(item, instance, log, line_id)
                    if is_processed:
                        is_processed = self.__find_order_tax(item, instance, log, line_id)
                        if is_processed:
                            vals = self._prepare_order_dict(item, instance)
                            magento_order = self.create(vals)
                            item.update({"sale_order_id": magento_order})
                            order_line.create_order_line(item, instance, log, line_id)
                            # self.__create_discount_order_line(item)
                            self.__create_shipping_order_line(item)
                            self.__create_delivery_isurance_order_line(item)
                            self.__create_zelle_payment_surcharge_order_line(item)
                            self._create_credit_line(item)
                            if item.get("status") == "canceled":
                                magento_order._action_cancel()
                                return is_processed
                            self.__process_order_workflow(item, log)
        return is_processed

    @staticmethod
    def __find_order_warehouse(item, log, line_id):
        is_processed = True
        if not item.get("website").warehouse_id.id:
            message = _(
                f"""
            Order {item['increment_id']} was skipped because warehouse is not set for the website
            {item['website'].name}. Please configure it from Magento2 Connector -> Configuration ->
            Setting -> Magento websites.
            """
            )
            log.write(
                {
                    "log_lines": [
                        (
                            0,
                            0,
                            {
                                "message": message,
                                "order_ref": item["increment_id"],
                                "magento_order_data_queue_line_id": line_id,
                            },
                        )
                    ]
                }
            )
            is_processed = False
        return is_processed

    def _find_price_list(self, item, log, line_id):
        is_processed = True
        price_list = False
        website_id = (
            self.env["magento.storeview"]
            .sudo()
            .search([("magento_storeview_id", "=", item.get("store_id"))])
            .magento_website_id
        )
        company_id = website_id.company_id
        currency = item.get("order_currency_code")
        currency_id = self._find_currency(currency)
        pricelist_id = website_id.pricelist_ids
        price_list = self.env["product.pricelist"].search(
            [("currency_id", "=", currency_id.id), ("company_id", "=", company_id.id)], limit=1
        )
        if price_list:
            pricelist_id = pricelist_id[0]
            item.update({"price_list_id": price_list})

        elif not price_list:
            magento_store = self.env["magento.storeview"].browse(item.get("store_id"))
            company = self.env["magento.storeview"].browse(item.get("store_id")).magento_website_id.company_id
            new_pricelist = pricelist_id.create(
                {
                    "company_id": company.id,
                    "currency_id": currency_id.id,
                    "name": f"{company.name} - {magento_store.name}",
                }
            )
            if new_pricelist:
                new_pricelist = new_pricelist[0]
                item.update({"price_list_id": new_pricelist})
            else:
                is_processed = False
                message = _(
                    f"""
                -Order {item.get('increment_id')} was skipped, as no pricelist was
                found for currency {currency_id.name}. \n
                -We recommend synchronizing metadata.\n
                -Please go to Magento2 connector -> Configuration -> Instance -> select Instance ->
                Click on 'Synchronize Metadata'
                """
                )
                log.write(
                    {
                        "log_lines": [
                            (
                                0,
                                0,
                                {
                                    "message": message,
                                    "order_ref": item.get("increment_id"),
                                    "magento_order_data_queue_line_id": line_id,
                                },
                            )
                        ]
                    }
                )
        return is_processed

    def _find_currency(self, currency_code):
        currency = self.env["res.currency"]
        currency = currency.with_context(active_test=False).search([("name", "=", currency_code)], limit=1)
        if not currency.active:
            currency.write({"active": True})
        return currency

    def __update_partner_dict(self, item, instance):
        addresses = []
        magento_store = instance.magento_website_ids.store_view_ids.filtered(
            lambda l: l.magento_storeview_id == str(item.get("store_id"))
        )
        m_customer_id = self.__get_customer_id(item)
        website_id = magento_store.magento_website_id.magento_website_id
        customers = {
            "instance_id": instance,
            "firstname": item.get("customer_firstname"),
            "lastname": item.get("customer_lastname"),
            "email": item.get("customer_email"),
            "website": magento_store.magento_website_id,
            "website_id": website_id and int(website_id) or "",
            "store_view": magento_store,
            "id": m_customer_id,
            "is_guest": item.get("customer_is_guest"),
            "is_faulty": not item.get("customer_is_guest") and not item.get("customer_id", False),
        }
        if not item.get("customer_firstname"):
            customers.update(
                {
                    "firstname": item.get("billing_address").get("firstname"),
                    "lastname": item.get("billing_address").get("lastname"),
                }
            )
        b_address = self.__update_partner_address_dict(customers, item.get("billing_address"))
        addresses.append(b_address)
        ship_assign = item.get("extension_attributes", dict()).get("shipping_assignments")
        for ship_addr in ship_assign:
            if isinstance(ship_addr, dict) and "address" in list(ship_addr.get("shipping", {}).keys()):
                ship_addr = ship_addr.get("shipping", dict()).get("address")
                s_address = self.__update_partner_address_dict(customers, ship_addr)
                addresses.append(s_address)
        customers.update({"addresses": addresses})
        item.update(customers)
        return customers

    @staticmethod
    def __get_customer_id(item):
        customer_id = item.get("customer_id", False)
        if item.get("customer_is_guest"):
            customer_id = "Guest Customer"
        elif not item.get("customer_is_guest") and not item.get("customer_id", False):
            customer_id = "Customer Without Id"
        return customer_id

    @staticmethod
    def __update_partner_address_dict(item, addresses):
        address = {
            "firstname": addresses.get("firstname"),
            "lastname": addresses.get("lastname"),
            "email": item.get("email"),
            "street": addresses.get("street"),
            "city": addresses.get("city"),
            "postcode": addresses.get("postcode"),
            "company": addresses.get("company", False),
            "id": addresses.get("customer_address_id") or addresses.get("entity_id"),
            "website_id": item.get("website_id"),
            "customer_id": item.get("id"),
            "region": {"region_code": addresses.get("region_code")},
            "country_id": addresses.get("country_id"),
            "telephone": addresses.get("telephone"),
        }
        if addresses.get("address_type") == "billing":
            address.update({"default_billing": True})
        if addresses.get("address_type") == "shipping":
            address.update({"default_shipping": True})
        return address

    def _prepare_order_dict(self, item, instance):
        store_view = item.get("store_view")
        website_company = item.get("website").company_id
        payment_method = self.env["magento.payment.method"].search([("id", "=", item.get("payment_gateway"))])
        sale_workflow = self.env["magento.financial.status.ept"].search(
            [
                ("company_id", "=", website_company.id),
                ("payment_term_id", "=", item.get("payment_term_id").id),
                ("payment_method_id", "=", payment_method.id),
            ]
        )
        if sale_workflow:
            policy = sale_workflow.auto_workflow_id.picking_policy
        else:
            policy = "one"
        address = ""
        if item.get("billing_address"):
            address = (
                item.get("billing_address").get("street")[0]
                + ","
                + (item.get("billing_address").get("city") if item.get("billing_address").get("city") else "")
                + ","
                + (item.get("billing_address").get("postcode") if item.get("billing_address").get("postcode") else "")
                + ","
                + (
                    item.get("billing_address").get("country_id")
                    if item.get("billing_address").get("country_id")
                    else ""
                )
            )

        resend_order = False
        is_resend_order = ""
        customer_order_nbr = False
        fraud_score = False
        customer_notes = ''
        if item.get("extension_attributes").get("amasty_order_attributes"):
            for amasty in item.get("extension_attributes").get("amasty_order_attributes"):
                if amasty.get("attribute_code") == "resend_reason":
                    is_resend_order = amasty.get("attribute_code")
                if amasty.get("attribute_code") == "customer_order_nbr":
                    customer_order_nbr = amasty.get("value")
        if is_resend_order == "resend_reason":
            resend_order = True
            resend_reason = amasty.get("label", "")
        else:
            resend_order = False
            resend_reason = False
        if "extension_attributes" in item and "fraudlabspro_score" in item['extension_attributes'] and item['extension_attributes']['fraudlabspro_score']:
            fraud_score = item['extension_attributes']['fraudlabspro_score']
        else:
            fraud_score = False
        if "extension_attributes" in item and "amasty_order_attributes" in item['extension_attributes'] and item['extension_attributes']['amasty_order_attributes']:
            for attr in item['extension_attributes']['amasty_order_attributes']:
                if attr['attribute_code'] == 'customer_notes':
                    customer_notes = attr['value']
        else:
            customer_notes = ''
        partner_id = self.env['res.partner'].browse(item.get("parent_id"))
        order_vals = {
            "company_id": website_company.id,
            "partner_id": item.get("parent_id"),
            "partner_invoice_id": item.get("invoice") if item.get("invoice") else item.get("parent_id"),
            "partner_shipping_id": item.get("delivery") if item.get("delivery") else item.get("parent_id"),
            "warehouse_id": item.get("website").warehouse_id.id,
            "picking_policy": policy,
            "date_order": item.get("created_at", False),
            "pricelist_id": item.get("price_list_id") and item.get("price_list_id").id or False,
            "team_id": store_view and store_view.team_id and store_view.team_id.id or False,
            "payment_term_id": item.get("payment_term_id").id,
            "carrier_id": item.get("delivery_carrier_id"),
            "client_order_ref": item.get("increment_id"),
            "note": customer_order_nbr,
            "user_id": partner_id.user_id and partner_id.user_id.id or False,
        }
        order_vals = self.create_sales_order_vals_ept(order_vals)
        order_vals = self.__update_order_dict(item, instance, order_vals)
        order_vals.update(
            {
                "magento_billing_address": address,
                "is_resend_order": resend_order,
                "resend_reason": resend_reason,
                "note": customer_order_nbr,
                "fraud_score":fraud_score,
                'note':customer_notes
            }
        )
        return order_vals

    def __update_order_dict(self, item, instance, order_vals):
        payment_info = item.get("extension_attributes").get("order_response")
        store_view = item.get("store_view")
        website_id = store_view.magento_website_id
        auto_workflow_process_id = item.get("workflow_id").filtered(lambda x: x.company_id == website_id.company_id).id
        if not auto_workflow_process_id:
            auto_workflow_process_id = False
        order_vals.update(
            {
                "name": str(item.get("increment_id")),
                "magento_instance_id": instance.id,
                "magento_website_id": website_id.id,
                "store_id": item.get("store_view").id,
                "auto_workflow_process_id": auto_workflow_process_id,
                "currency_id": item.get("currency_id", False),
                "magento_payment_method_id": item.get("payment_gateway"),
                "magento_payment_code": item.get("payment_code"),
                "magento_shipping_method_id": item.get("magento_carrier_id"),
                "is_exported_to_magento_shipment_status": False,
                "magento_order_id": item.get("entity_id"),
                "magento_order_reference": item.get("increment_id"),
                "order_transaction_id": self.__find_transaction_id(payment_info),
                "analytic_account_id": instance.magento_analytic_account_id
                and instance.magento_analytic_account_id.id
                or False,
                "magento_status": item.get("status"),
            }
        )
        if store_view and not store_view.is_use_odoo_order_sequence:
            name = "{}{}".format(
                store_view and store_view.sale_prefix or "",
                str(item.get("increment_id")),
            )
            order_vals.update({"name": name})
        return order_vals

    @staticmethod
    def __find_transaction_id(payment_info):
        payment_additional_info = payment_info if payment_info else False
        transaction_id = False
        if payment_additional_info:
            for payment_info in payment_additional_info:
                if payment_info.get("key") == "transaction_id":
                    transaction_id = payment_info.get("value")
        return transaction_id

    def __create_shipping_order_line(self, item):
        order_line = self.env["sale.order.line"]
        incl_amount = float(item.get("shipping_incl_tax", 0.0))
        excl_amount = float(item.get("shipping_amount", 0.0))
        excl_amount = 0.00
        if item.get("base_currency_code") != item.get("order_currency_code"):
            excl_amount = float(item.get("shipping_amount", 0.0))
        else:
            excl_amount = float(item.get("base_shipping_amount", 0.0))
        sale_order_id = item.get("sale_order_id")
        if incl_amount or excl_amount:
            tax_type = self.__find_tax_type(item.get("extension_attributes"), "apply_shipping_on_prices")
            price = incl_amount if tax_type else excl_amount
            default_product = self.env.ref("odoo_magento2_ept.product_product_shipping")
            self.env.ref("odoo_magento2_ept.product_product_shipping")
            product = sale_order_id.magento_instance_id.shipping_product_id or default_product
            shipping_line = order_line.prepare_order_line_vals(item, {}, product, price)
            shipping_line.update({"is_delivery": True})
            if item.get("shipping_tax"):
                shipping_line.update({"tax_id": [(6, 0, item.get("shipping_tax"))]})
            if item["extension_attributes"]["applied_taxes"] == []:
                partner_country = item.get("sale_order_id").partner_shipping_id.country_id
                website_tax_country_line = item.get("website").tax_country_line_ids.filtered(lambda webline: partner_country == webline.country_id)
                shipping_line.update({"tax_id": [(6, 0, website_tax_country_line and website_tax_country_line.tax_id.ids or [])]})
            order_line.create(shipping_line)
        return True

    def __create_delivery_isurance_order_line(self, item):
        order_line = self.env["sale.order.line"]
        float(item.get("shipping_incl_tax", 0.0))
        float(item.get("shipping_amount", 0.0))
        sale_order_id = item.get("sale_order_id")
        delivery_isurance = item.get("extension_attributes").get("amextrafee_fee_id")
        base_delivery_isurance = item.get("extension_attributes").get("amextrafee_base_fee_amount")
        if delivery_isurance or base_delivery_isurance:
            price = 0.00
            if item.get("base_currency_code") != item.get("order_currency_code"):
                price = item.get("extension_attributes").get("amextrafee_fee_amount")
            else:
                price = item.get("extension_attributes").get("amextrafee_base_fee_amount")
            product = sale_order_id.magento_instance_id.delivery_isurance_product_id.product_variant_id
            line_vals = order_line.prepare_order_line_vals(item, {}, product, price)
            order_line.create(line_vals)
        return True

    def __create_zelle_payment_surcharge_order_line(self, item):
        order_line = self.env["sale.order.line"]
        price = 0.0
        surcharge = item.get("extension_attributes").get("fooman_total_group")
        if surcharge:
            for sur in surcharge.get("items"):
                price = sur.get("amount")
                if price:
                    sale_order_id = item.get("sale_order_id")
                    default_product = self.env.ref("odoo_magento2_ept.product_product_shipping")
                    self.env.ref("odoo_magento2_ept.product_product_shipping")
                    product = (
                        sale_order_id.magento_instance_id.surcharge_product_id.product_variant_id or default_product
                    )
                    payment_line = order_line.prepare_order_line_vals(item, {}, product, price)
                    order_line.create(payment_line)
        return True

    def _create_credit_line(self, item):
        order_line = self.env["sale.order.line"]
        item.get("sale_order_id")
        balance_amount = 0.00
        if item.get("base_currency_code") != item.get("order_currency_code"):
            balance_amount = item.get("extension_attributes").get("customer_balance_amount", False)
        else:
            balance_amount = item.get("extension_attributes").get("base_customer_balance_amount", False)
        product_tmpl_id = self.env["product.template"].search(
            [("name", "=", "Store Credit"), ("detailed_type", "=", "service")], limit=1
        )
        if not product_tmpl_id:
            val = {"name": "Store Credit", "detailed_type": "service", "default_code": "Store Credit"}
            product_tmpl_id = self.env["product.template"].create(val)
        product_id = self.env["product.product"].search([("product_tmpl_id", "=", product_tmpl_id.id)])
        if balance_amount and balance_amount > 0:
            line_vals = order_line.prepare_order_line_vals(item, {}, product_id, -balance_amount)
            order_line.create(line_vals)
        return True

    def __find_shipping_tax_percent(self, tax_details, ext_attrs):
        if "item_applied_taxes" in ext_attrs:
            tax_type = self.__find_tax_type(ext_attrs, "apply_shipping_on_prices")
            for order_res in ext_attrs.get("item_applied_taxes"):
                if order_res.get("type") == "shipping" and order_res.get("applied_taxes"):
                    for tax in order_res.get("applied_taxes", list()):
                        tax_details.append(
                            {
                                "line_tax": "shipping_tax",
                                "tax_type": tax_type,
                                "tax_title": tax.get("title"),
                                "tax_percent": tax.get("percent", 0),
                            }
                        )
        return tax_details

    def __find_tax_percent_title(self, item, instance):
        tax_details = []
        if instance.magento_apply_tax_in_order == "create_magento_tax":
            if "apply_discount_on_prices" in item.get("extension_attributes"):
                tax_type = self.__find_tax_type(item.get("extension_attributes"), "apply_discount_on_prices")
                tax_percent = self.__find_discount_tax_percent(item.get("items"))
                if tax_percent:
                    tax_name = "%s %% " % tax_percent
                    tax_details.append(
                        {
                            "line_tax": "discount_tax",
                            "tax_type": tax_type,
                            "tax_title": tax_name,
                            "tax_percent": tax_percent,
                        }
                    )
            if "apply_shipping_on_prices" in item.get("extension_attributes"):
                ext_attrs = item.get("extension_attributes")
                tax_details = self.__find_shipping_tax_percent(tax_details, ext_attrs)
            # else:
            for line in item.get("items"):
                tax_percent = line.get("tax_percent", 0.0)
                parent_item = line.get("parent_item", {})
                if parent_item and parent_item.get("product_type") != "bundle":
                    tax_percent = line.get("parent_item", {}).get("tax_percent", 0.0)
                if tax_percent:
                    tax_name = "%s %% " % tax_percent
                    tax_type = item.get("website").tax_calculation_method == "including_tax"
                    tax_details.append(
                        {
                            "line_tax": f'order_tax_{line.get("item_id")}',
                            "tax_type": tax_type,
                            "tax_title": tax_name,
                            "tax_percent": tax_percent,
                        }
                    )
        return tax_details

    @staticmethod
    def __find_tax_type(ext_attrs, tax):
        tax_type = False
        if tax in ext_attrs:
            tax_price = ext_attrs.get(tax)
            if tax_price == "including_tax":
                tax_type = True
        return tax_type

    def __create_discount_order_line(self, item):
        order_line = self.env["sale.order.line"]
        sale_order_id = item.get("sale_order_id")
        price = float(item.get("discount_amount") or 0.0) or False
        if price:
            default_product = self.env.ref("odoo_magento2_ept.magento_product_product_discount")
            product = sale_order_id.magento_instance_id.discount_product_id or default_product
            line = order_line.prepare_order_line_vals(item, {}, product, price)
            # if item.get("discount_tax"):
            #     line.update({"tax_id": [(6, 0, item.get("discount_tax"))]})
            order_line.create(line)
        return True

    @staticmethod
    def __find_discount_tax_percent(items):
        percent = False
        for item in items:
            percent = item.get("tax_percent") if "tax_percent" in item.keys() and item.get("tax_percent") > 0 else False
            if percent:
                break
        return percent

    def __find_order_tax(self, item, instance, log, line_id):
        order_line = self.env["sale.order.line"]
        account_tax_obj = self.env["account.tax"]
        tax_details = self.__find_tax_percent_title(item, instance)
        tax_id_list = []
        for tax in tax_details:
            tax_id = account_tax_obj.get_tax_from_rate(
                float(tax.get("tax_percent")), tax.get("tax_title"), tax.get("tax_type"), item.get("website")
            )
            if tax_id and not tax_id.active:
                message = _(
                    f"""
                Order {item['increment_id']} was skipped because the tax {tax_id.name}% was not found.
                The connector is unable to create new tax {tax_id.name}%, kindly check the tax
                {tax_id.name}% has been archived?
                """
                )
                log.write(
                    {
                        "log_lines": [
                            (
                                0,
                                0,
                                {
                                    "message": message,
                                    "order_ref": item["increment_id"],
                                    "magento_order_data_queue_line_id": line_id,
                                },
                            )
                        ]
                    }
                )
                return False
            if not tax_id:
                tax_vals = order_line.prepare_tax_dict(tax, instance)
                tax_id = account_tax_obj.sudo().create(tax_vals)
            if tax.get("line_tax") != "shipping_tax":

                item.update({tax.get("line_tax"): tax_id.ids})
            else:
                tax_id_list.append(tax_id.id)
        if tax_id_list:
            item.update({"shipping_tax": tax_id_list})
        return True

    def __process_order_workflow(self, item, log):
        sale_workflow = self.env["sale.workflow.process.ept"]
        sale_order = item.get("sale_order_id")
        # if item.get("status") == "complete" or (
        #     item.get("status") == "processing" and item.get("extension_attributes").get("is_shipment")
        # ):
        #     sale_order.auto_workflow_process_id.with_context(log_book_id=log.id).shipped_order_workflow_ept(sale_order)
        # else:
        sale_workflow.with_context(log_book_id=log.id).auto_workflow_process_ept(
            sale_order.auto_workflow_process_id.id, [sale_order.id]
        )
        if (
            item.get("status") == "complete"
            or (item.get("status") == "processing" and item.get("extension_attributes").get("is_invoice"))
            and sale_order.invoice_ids
        ):
            # Here the magento order is complete state or
            # processing state with invoice so invoice is already created
            # So Make the Export invoice as true to hide Export invoice button from invoice.
            sale_order.invoice_ids.write({"is_exported_to_magento": True})

    def cancel_order_from_magento(self):
        """
        this method will call while sale order cancel from webhook
        :return:
        """
        log_msg = ""
        result = False
        try:
            result = super(SaleOrder, self).action_cancel()
        except Exception as error:
            log_msg = error
        if not result:
            message = "Order {} could not be cancelled in Odoo via webhook. \n".format(
                self.magento_order_reference
            ) + str(log_msg)
            model_id = self.env["common.log.lines.ept"].sudo().get_model_id("sale.order")
            self.env["common.log.book.ept"].sudo().create(
                {
                    "type": "import",
                    "module": "magento_ept",
                    "model_id": model_id,
                    "res_id": self.id,
                    "magento_instance_id": self.magento_instance_id.id,
                    "log_lines": [
                        (
                            0,
                            0,
                            {
                                "message": message,
                                "order_ref": self.name,
                            },
                        )
                    ],
                }
            )
        return True

    def import_cancel_order(self, **kwargs):
        """
        This method use for import cancel order from magento.
        @:return:result
        :return:
        """
        instance = kwargs.get("instance")
        order_queue = self.env["magento.order.data.queue.ept"]
        orders = order_queue._get_order_response(instance, kwargs, False)
        for order in orders["items"]:
            order_id = order.get("entity_id", 0)
            sale_order = self.search(
                [("magento_instance_id", "=", instance.id), ("magento_order_id", "=", str(order_id))], limit=1
            )
            if sale_order:
                sale_order.sudo().cancel_order_from_magento()
        return True

    def cancel_order_in_magento(self):
        """
        This method use for cancel order in magento.
        @return: result
        """
        magento_order_id = self.magento_order_id
        if magento_order_id:
            magento_instance = self.magento_instance_id
            try:
                api_url = "/V1/orders/%s/cancel" % magento_order_id
                result = req(magento_instance, api_url, "POST")
            except Exception:
                raise UserError(_("Error while requesting cancel order"))
        return result

    def action_cancel(self):
        super(SaleOrder, self).action_cancel()
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "cancel.sale",
            "target": "new",
            "context": {
                "default_sale_id": self.id,
            },
        }

    def _prepare_invoice(self):
        """
        This method is used for set necessary value(is_magento_invoice,
        is_exported_to_magento,magento_instance_id) in invoice.
        :return:
        """
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if self.magento_payment_method_id:
            invoice_vals["magento_payment_method_id"] = self.magento_payment_method_id.id
        if self.magento_instance_id:
            invoice_vals.update(
                {
                    "magento_instance_id": self.magento_instance_id.id,
                    "is_magento_invoice": True,
                    "is_exported_to_magento": False,
                }
            )
        return invoice_vals

    def open_order_in_magento(self):
        """
        This method is used for open order in magento
        """
        m_url = self.magento_instance_id.magento_admin_url
        m_order_id = self.magento_order_id
        if m_url:
            return {
                "type": "ir.actions.act_url",
                "url": "{}/sales/order/view/order_id/{}".format(m_url, m_order_id),
                "target": "new",
            }

    def _action_cancel(self):
        documents = None
        for sale_order in self:
            if sale_order.state == "sale" and sale_order.order_line:
                sale_order_lines_quantities = {
                    order_line: (order_line.product_uom_qty, 0) for order_line in sale_order.order_line
                }
                documents = (
                    self.env["stock.picking"]
                    .with_context(include_draft_documents=True)
                    ._log_activity_get_documents(sale_order_lines_quantities, "move_ids", "UP")
                )
        # self.picking_ids.filtered(lambda p: p.state in ['draft','ready']).action_cancel()
        for rec in self.picking_ids:
            if rec.state in ["draft", "assigned", "waiting", "confirmed"]:
                rec.action_cancel()
        if documents:
            filtered_documents = {}
            for (parent, responsible), rendering_context in documents.items():
                if parent._name == "stock.picking":
                    if parent.state == "cancel":
                        continue
                filtered_documents[(parent, responsible)] = rendering_context
            self._log_decrease_ordered_quantity(filtered_documents, cancel=True)
        return super()._action_cancel()
