# See LICENSE file for full copyright and licensing details.
"""
Describes methods to store Order Data queue line
"""
import json
import pytz
from odoo import _, fields, models
from dateutil import parser

utc = pytz.utc


class MagentoOrderDataQueueLineEpt(models.Model):
    """
    Describes Order Data Queue Line
    """

    _name = "magento.order.data.queue.line.ept"
    _description = "Magento Order Data Queue Line EPT"
    _rec_name = "magento_id"

    queue_id = fields.Many2one(comodel_name="magento.order.data.queue.ept", ondelete="cascade")
    instance_id = fields.Many2one(
        comodel_name="magento.instance", string="Magento Instance", help="Order imported from this Magento Instance."
    )
    state = fields.Selection(
        [("draft", "Draft"), ("failed", "Failed"), ("done", "Done"), ("cancel", "Cancelled")],
        default="draft",
        copy=False,
    )
    magento_id = fields.Char(string="Magento Order#", help="Id of imported order.", copy=False)
    sale_order_id = fields.Many2one(comodel_name="sale.order", copy=False, help="Order created in Odoo.")
    data = fields.Text(help="Data imported from Magento of current order.", copy=False)
    processed_at = fields.Datetime(
        string="Processed At", copy=False, help="Shows Date and Time, When the data is processed"
    )
    log_lines_ids = fields.One2many(
        "common.log.lines.ept", "magento_order_data_queue_line_id", help="Log lines created against which line."
    )
    company_id = fields.Many2one("res.company", string="Company")
    website_id = fields.Many2one("magento.website", string="Website")

    def open_sale_order(self):
        """
        call this method while click on > Order Data Queue line > Sale Order smart button
        :return: Tree view of the odoo sale order
        """
        return {
            "name": "Sale Order",
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "view_type": "form",
            "view_mode": "tree,form",
            "domain": [("id", "=", self.sale_order_id.id)],
        }

    def create_order_queue_line(self, instance, order, queue):
        website_id = (
            self.env["magento.storeview"]
            .search([("magento_storeview_id", "=", order.get("store_id"))])
            .magento_website_id
        )
        company_id = website_id.company_id
        available_website = self.env["magento.website"].search(
            [("id", "=", website_id.id), ("company_id", "=", company_id.id)]
        )
        if available_website:
            # if not website_id.short_code:
            #     raise UserError(_(f"Please Enter the Short Code for the Website {website_id.name}."))
            self.create(
                {
                    "magento_id": order.get("increment_id"),
                    "instance_id": instance.id,
                    "data": json.dumps(order),
                    "queue_id": queue.id,
                    "company_id": company_id.id,
                    "website_id": website_id.id,
                }
            )
            queue.company_id = company_id.id
            return True
        else:
            return False

    def auto_import_order_queue_data(self):
        """
        This method used to process synced magento order data in batch of 50 queue lines.
        This method is called from cron job.
        """
        queues = self.env["magento.order.data.queue.line.ept"].search([("state", "=", "draft")]).mapped("queue_id")
        queues.process_order_queues()

    def process_order_queue_line(self, line, log):
        item = json.loads(line.data)
        order_ref = item.get("increment_id")
        order = self.env["sale.order"]
        instance = self.instance_id
        coming_status = item.get("status", False)
        is_exists = order.search(
            [("magento_instance_id", "=", instance.id), ("magento_order_reference", "=", order_ref)], limit=1
        )
        payment_method = item.get("payment", dict()).get("method")
        website_id = self.env["magento.storeview"].search([("magento_storeview_id", "=", item.get("store_id"))]).magento_website_id
        if is_exists:
            incoming_status = item.get("status", False)
            if incoming_status and incoming_status != is_exists.magento_status:
                if incoming_status == "canceled":
                    is_exists._action_cancel()
                    is_exists.write({"magento_status": incoming_status})
                elif incoming_status == "processing" and is_exists.invoice_status != "invoiced":
                    self.process_autoworkflow_update_saleorder(is_exists, item, log, line)
                    is_exists.write({"magento_status": incoming_status})
            return True
        create_at = item.get("created_at", False)
        # Need to compare the datetime object
        date_order = parser.parse(create_at).astimezone(utc).strftime("%Y-%m-%d %H:%M:%S")
        if str(instance.import_order_after_date) > date_order:
            message = _(
                f"""
            There is a configuration mismatch in the import of order #{order_ref}.\n
            The order receive date is {date_order}.\n
            Please check the date set in the configuration in Magento2 Connector -> Configuration
            -> Setting -> Select Instance -> 'Import Order After Date'.
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
                                "order_ref": line.magento_id,
                                "magento_order_data_queue_line_id": line.id,
                            },
                        )
                    ]
                }
            )
            return False
        is_processed = self.financial_status_config(item, instance, log, line)
        if is_processed:
            carrier = self.env["delivery.carrier"]
            is_processed = carrier.find_delivery_carrier(item, instance, log, line)
            if is_processed:
                # add create product method
                item_ids = self.__prepare_product_dict(item.get("items"))
                m_product = self.env["magento.product.product"]
                p_items = m_product.with_context(is_order=True).get_products(instance, item_ids, line)

                order_item = self.env["sale.order.line"].find_order_item(item, instance, log, line.id)
                if not order_item:
                    if p_items:
                        p_queue = self.env["sync.import.magento.product.queue.line"]
                        self._update_product_type(p_items, item)
                        for p_item in p_items:
                            is_processed = p_queue.with_context(is_order=True).import_products(p_item, line)
                            if not is_processed:
                                break
                    else:
                        is_processed = False
                if is_processed:
                    if payment_method == "btcpay" and website_id.magento_website_id in ['6','5','7']:
                        if coming_status in [
                            "btcpay_paid_correctly",
                            "btcpay_underpaid",
                            "btcpay_overpaid",
                            "complete",
                            "processing",
                        ]:
                            is_processed = order.create_sale_order_ept(item, instance, log, line.id)
                            if is_processed:
                                line.write({"sale_order_id": item.get("sale_order_id").id})
                        else:
                            is_processed = False
                    elif payment_method == "oppcw_creditcard":
                        if coming_status in ["processing","pending_payment"]:
                            is_processed = order.create_sale_order_ept(item, instance, log, line.id)
                            if is_processed:
                                line.write({"sale_order_id": item.get("sale_order_id").id})
                    elif payment_method == "paragon":
                        if coming_status in ["processing"]:
                            is_processed = order.create_sale_order_ept(item, instance, log, line.id)
                            if is_processed:
                                line.write({"sale_order_id": item.get("sale_order_id").id})
                    else:
                        is_processed = order.create_sale_order_ept(item, instance, log, line.id)
                        if is_processed:
                            line.write({"sale_order_id": item.get("sale_order_id").id})
        return is_processed

    def process_autoworkflow_update_saleorder(self, order, item, log, line):
        self.financial_status_config(item, self.instance_id, log, line)
        if (
            item.get("extension_attributes", False)
            and item["extension_attributes"].get("payment_additional_info", False)
            and item["extension_attributes"]["payment_additional_info"][0].get("value", False)
        ):
            for _payment_key, payment_val in item["extension_attributes"]["payment_additional_info"][0].items():
                if payment_val == "raw_details_info":
                    payment_code = json.loads(item["extension_attributes"]["payment_additional_info"][0]["value"]).get(
                        "payment_code", False
                    )
                    if self.company_id.id == 10:
                        if payment_code:
                            order.write({"magento_payment_code": payment_code})
                            order.write({"auto_workflow_process_id": item.get("workflow_id").id})
                            order.validate_and_paid_invoices_ept(item.get("workflow_id"))
        else:
            f_status = self.env["magento.financial.status.ept"]
            method = item.get("payment", dict()).get("method")
            gateway = self.instance_id.payment_method_ids.filtered(lambda x: x.payment_method_code == method)
            f_status = f_status.search_financial_status(item, self.instance_id, gateway)
            workflow = f_status.get("workflow").filtered(lambda fin_stat: fin_stat.company_id == self.env.company)
            order.write({"auto_workflow_process_id": workflow.auto_workflow_id.id})
            order.validate_and_paid_invoices_ept(workflow.auto_workflow_id)

    @staticmethod
    def __prepare_product_dict(items):
        parent_id, item_ids = [], []
        for item in items:
            e_attribute = item.get("extension_attributes", {})
            product_id = item.get("product_id")
            if e_attribute.get("simple_parent_id"):
                product_id = e_attribute.get("simple_parent_id")
            if product_id not in item_ids:
                item_ids.append(product_id)
        return item_ids

    @staticmethod
    def _update_product_type(p_items, items):
        for p_item in p_items:
            for item in items.get("items"):
                if item.get("product_id") == p_item.get("id"):
                    p_item.update({"type_id": item.get("product_type"), "increment_id": items.get("increment_id")})
        return True

    def financial_status_config(self, item, instance_id, log, line):
        is_processed = True
        payment_code = "payment_code"
        f_status = self.env["magento.financial.status.ept"]
        method = item.get("payment", dict()).get("method")
        gateway = instance_id.payment_method_ids.filtered(lambda x: x.payment_method_code == method)
        gateway.payment_method_name
        f_status = f_status.search_financial_status(item, instance_id, gateway)
        workflow = f_status.get("workflow")
        f_status.get("status_name")
        message = ""
        if not is_processed:
            log.write(
                {
                    "log_lines": [
                        (
                            0,
                            0,
                            {
                                "message": message,
                                "order_ref": line.magento_id,
                                "magento_order_data_queue_line_id": line.id,
                            },
                        )
                    ]
                }
            )
        else:
            item.update(
                {
                    "workflow_id": workflow.auto_workflow_id,
                    "payment_term_id": workflow.payment_term_id,
                    "payment_gateway": gateway.id,
                }
            )
            if (
                item.get("extension_attributes", False)
                and item["extension_attributes"].get("payment_additional_info", False)
                and item["extension_attributes"]["payment_additional_info"][0].get("value", False)
            ):
                for payment_dict in item["extension_attributes"]["payment_additional_info"]:
                    for _payment_key, payment_val in payment_dict.items():
                        if payment_val == "raw_details_info":
                            payment_value = json.loads(
                                item["extension_attributes"]["payment_additional_info"][0]["value"]
                            )
                            if payment_code in payment_value:
                                payment_code = json.loads(
                                    item["extension_attributes"]["payment_additional_info"][0]["value"]
                                ).get("payment_code", False)
                            if self.company_id.id == 10:
                                if method == "paragon":
                                    payment_method_code_id = self.env["payment.method.code"].search(
                                        [("payment_code", "=", method)]
                                    )
                                    item.update(
                                        {
                                            "payment_code": method,
                                            "workflow_id": payment_method_code_id.workflow_id,
                                        }
                                    )
                                    break
                                if payment_code:
                                    payment_method_code_id = self.env["payment.method.code"].search(
                                        [("payment_code", "=", payment_code)]
                                    )
                                    item.update(
                                        {
                                            "payment_code": payment_code,
                                            "workflow_id": payment_method_code_id.workflow_id,
                                        }
                                    )
                                    break
                        if payment_val == "processor_id":
                            payment_code = payment_dict.get("value", False)
                            if payment_code:
                                payment_method_code_id = self.env["payment.method.code"].search(
                                    [("payment_code", "=", payment_code)]
                                )
                                item.update(
                                    {
                                        "payment_code": payment_code,
                                        "workflow_id": payment_method_code_id.workflow_id,
                                    }
                                )
                                break
                        if method == "paragon":
                            payment_method_code_id = self.env["payment.method.code"].search(
                                [("payment_code", "=", method)]
                            )
                            item.update(
                                {
                                    "payment_code": method,
                                    "workflow_id": payment_method_code_id.workflow_id,
                                }
                            )
                            
                        if method == "btcpay" and item.get("status", False) == "btcpay_underpaid":
                            payment_method_code_id = self.env["payment.method.code"].search(
                                        [("payment_code", "=", 'btcpay_underpaid')], limit=1
                                    )
                            item.update({
                                    "payment_code": method,
                                    "workflow_id": payment_method_code_id.workflow_id,
                                }
                            )
        return is_processed

    @staticmethod
    def check_mismatch_order(item):
        is_inv = item.get("extension_attributes").get("is_invoice")
        is_ship = item.get("extension_attributes").get("is_shipment")
        if not is_inv and not is_ship and item.get("status") == "processing":
            message = _(
                f"""
            Order {item.get('increment_id')} was skipped, Order status is processing,
            but the order is neither invoice nor shipped.
            """
            )
        elif item.get("status") not in ["pending", "processing", "complete"]:
            message = _(
                """
            Order {item.get('increment_id')} was skipped due to financial status not found of
            order status {item.get('status')}.\n
            Currently the Magento2 Odoo Connector supports magento default order status
            such as 'Pending', 'Processing' and 'Completed'.
            The connector does not support the magento2 custom order status {item.get('status')}.
            """
            )
        else:
            message = _(
                """
            Order {item.get('increment_id')} was skipped because the order is partially invoiced
            and partially shipped.\n Magento order status Processing: Processing means that orders
            have either been invoiced or shipped, but not both.\n In this, we are receiving
            order in which it is partially invoiced and partially shipped.
            """
            )
        return False, message
