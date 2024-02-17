import requests
import json
from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_diamond_logistic_order = fields.Boolean("Is Diamond Logistic Order")
    is_diamond_logistic_order_send = fields.Boolean("Is Diamond Logistic Order Send", copy=False)
    diamond_logistic_order_id = fields.Char("Diamond Logistic Order ID", copy=False)
    diamond_logistic_response_message = fields.Char("Diamond Logistic Response Message", copy=False)

    def create_despatchlab_order(self):
        diamond_warehouses = self.env["stock.warehouse"].search([("is_despatchlab_warehouse", "=", True)])
        for order in self.filtered(lambda o: o.is_diamond_logistic_order and o.warehouse_id in diamond_warehouses):
            can_be_send = False
            if order.invoice_status == "to invoice" and order.resend_reason:
                can_be_send = True
            elif order.invoice_status == "invoiced":
                can_be_send = True
            if can_be_send:
                token_url = "https://api.despatchlab.tech/v1/auth/token/credentials"
                header = {
                    "Content-Type": "application/json",
                }
                log_book = self.env["common.log.book.ept"].search([], limit=1)
                if not log_book:
                    log_book = self.env["common.log.book.ept"].create({})
                data = {
                    "key": f"{order.company_id.despatchlab_username}",
                    "secret": f"{order.company_id.despatchlab_password}",
                }
                response = requests.post(token_url, data=json.dumps(data), headers=header)
                token = False
                if response.status_code in [200]:
                    response_dict = json.loads(response.text)
                    token = response_dict["tokens"]["access"]
                else:
                    raise ValidationError(_("Failed to get token, authorization failed."))
                order_create_url = "https://api.despatchlab.tech/v1/warehouse/orders"
                order_create_header = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(token),
                }
                product_datas = []
                for line in order.order_line.filtered(lambda ol: ol.product_id.detailed_type == "product"):
                    product_data = {"sku": line.product_id.default_code, "quantity": int(line.product_uom_qty)}
                    product_datas.append(product_data)
                order_data = {
                    "printDespatchNote": "true",
                    "addPackagingToOrder": "false",
                    # "address": 0,
                    "addressLine1": order.partner_shipping_id.street if order.partner_shipping_id.street else "",
                    "addressLine2": order.partner_shipping_id.street2 if order.partner_shipping_id.street2 else "",
                    "addressLine3": "",
                    "companyName": order.partner_shipping_id.name
                    if order.partner_shipping_id.name
                    else order.partner_id.name,
                    # "countryId": order.partner_shipping_id.country_id.name if order.partner_shipping_id.country_id.name else "",
                    "countryId": 1,
                    "countyOrState": order.partner_shipping_id.state_id.name
                    if order.partner_shipping_id.state_id.name
                    else "",
                    "customerId": order.company_id.diamond_logistics_customer_id,
                    "customerReference": order.name if order.name else "",
                    "deliveryType": "Overnight",
                    "feature": "48 Hour",
                    # "latitude": 0,
                    "locationType": "Business",
                    # "longitude": 0,
                    "postcodeOrZip": order.partner_shipping_id.zip if order.partner_shipping_id.zip else "",
                    "postcodeSearch": order.partner_shipping_id.zip.lower() if order.partner_shipping_id.zip else "",
                    "products": product_datas,
                    "recipientEmail": order.partner_shipping_id.email,
                    "recipientName": order.partner_shipping_id.name,
                    "recipientNumber": "",
                    "serviceType": "48 Hour",
                    "townOrCity": order.partner_shipping_id.city if order.partner_shipping_id.city else "",
                }
                response = requests.post(order_create_url, data=json.dumps(order_data), headers=order_create_header)
                if response.status_code in [200]:
                    order.diamond_logistic_order_id = response.text
                    order.is_diamond_logistic_order_send = True
                    order.diamond_logistic_response_message = False
                else:
                    order.diamond_logistic_order_id = False
                    order.is_diamond_logistic_order_send = False
                    order.diamond_logistic_response_message = response.text
                log_book.write(
                    {
                        "log_lines": [
                            (
                                0,
                                0,
                                {
                                    "message": response.text,
                                    "api_url": order_create_url,
                                    "api_data_sent": json.dumps(order_data),
                                },
                            )
                        ]
                    }
                )

    def action_confirm(self):
        diamond_warehouses = self.env["stock.warehouse"].search([("is_despatchlab_warehouse", "=", True)])
        result = super(SaleOrder, self).action_confirm()
        for order in self.filtered(
            lambda o: o.is_diamond_logistic_order and o.magento_payment_code and o.warehouse_id in diamond_warehouses
        ):
            order.create_despatchlab_order()
        return result

    def send_diamond_logistics_order_cron(self):
        diamond_warehouses = self.env["stock.warehouse"].search([("is_despatchlab_warehouse", "=", True)])
        diamond_orders = self.env["sale.order"].search(
            [
                ("is_diamond_logistic_order", "=", True),
                ("is_diamond_logistic_order_send", "=", False),
                ("magento_payment_code", "!=", False),
                ("warehouse_id", "in", diamond_warehouses.ids),
            ]
        )
        for order in diamond_orders:
            if any(order.picking_ids.mapped("state")) not in ["done", "cancel"] or any(
                order.picking_ids.mapped("location_id")
            ) in diamond_warehouses.mapped("lot_stock_id"):
                order.create_despatchlab_order()

    def _prepare_order_dict(self, item, instance):
        res = super(SaleOrder, self)._prepare_order_dict(item, instance)
        website = item.get("website", False)
        partner_shipping = self.env["res.partner"].browse(res["partner_shipping_id"])
        despatchlab_conf_customer_ids = self.env.company.despatchlab_partner_ids
        despatchlab_conf_warehouse_id = self.env.company.despatchlab_warehouse_id
        partner_country = partner_shipping.country_id
        website_delivery_country_line = website.delivery_country_line_ids.filtered(
            lambda webline: partner_country in webline.country_ids
        )
        partner_code = item.get("customer_id", False)
        despatchlab_conf_customer_codes = []
        for dl_customer in despatchlab_conf_customer_ids:
            code_line = dl_customer.magento_res_partner_ids.mapped("magento_customer_id")
            if code_line:
                despatchlab_conf_customer_codes.append(int(code_line[0]))
        if partner_code in despatchlab_conf_customer_codes:
            res["warehouse_id"] = despatchlab_conf_warehouse_id.id
            if despatchlab_conf_warehouse_id.is_despatchlab_warehouse:
                res["is_diamond_logistic_order"] = True
        elif website_delivery_country_line:
            res["warehouse_id"] = website_delivery_country_line[0].warehouse_id.id
            if website_delivery_country_line[0].warehouse_id.is_despatchlab_warehouse:
                res["is_diamond_logistic_order"] = True
        else:
            res["warehouse_id"] = website.warehouse_id.id
            if website.warehouse_id.is_despatchlab_warehouse:
                res["is_diamond_logistic_order"] = True
        return res

    def get_despatchlab_shipment_cron(self):
        log_book = self.env["common.log.book.ept"].search([], limit=1)
        if not log_book:
            log_book = self.env["common.log.book.ept"].create({})
        token_url = "https://api.despatchlab.tech/v1/auth/token/credentials"
        header = {
            "Content-Type": "application/json",
        }
        data = {
            "key": f"{self.env.company.despatchlab_username}",
            "secret": f"{self.env.company.despatchlab_password}",
        }
        response = requests.post(token_url, data=json.dumps(data), headers=header)
        token = False
        if response.status_code in [200]:
            response_dict = json.loads(response.text)
            token = response_dict["tokens"]["access"]
        else:
            raise ValidationError(_("Failed to get token, authorization failed."))
        order_url = "https://api.despatchlab.tech/v1/warehouse/orders"
        order_header = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token),
        }
        orders = self.env["sale.order"].search(
            [("is_diamond_logistic_order_send", "=", True), ("date_order", ">", datetime(2023, 6, 26))]
        )
        diamond_warehouses = self.env["stock.warehouse"].search([("is_despatchlab_warehouse", "=", True)])
        for order in orders:
            api_url = f"{order_url}/{order.diamond_logistic_order_id[1:-1]}"
            response = requests.get(api_url, data="", headers=order_header)
            picking_ids = order.picking_ids.filtered(
                lambda pick: pick.state not in ["done", "cancel"]
                and pick.location_id in diamond_warehouses.mapped("lot_stock_id")
            )
            if response.status_code in [200]:
                for picking in picking_ids:
                    result = json.loads(response.text)
                    picking.diamond_carrier = result.get("carrierName") if result.get("carrierName", False) else ""
                    picking.carrier_tracking_ref = (
                        result.get("shipmentNumber") if result.get("shipmentNumber", False) else ""
                    )
                    picking.diamond_shipment_id = result.get("shipmentId") if result.get("shipmentId", False) else ""
                    if picking.carrier_tracking_ref:
                        transfer = self.env["stock.immediate.transfer"].create(
                            {
                                "pick_ids": [(4, picking.id)],
                                "immediate_transfer_line_ids": [
                                    (0, 0, {"to_immediate": True, "picking_id": picking.id})
                                ],
                            }
                        )
                        transfer.with_context(button_validate_picking_ids=picking.id).process()
            if picking_ids:
                data_applied = {
                    "order": order.diamond_logistic_order_id,
                    "diamond_carrier": result.get("carrierName") if result.get("carrierName", False) else "",
                    "carrier_tracking_ref": result.get("shipmentNumber") if result.get("shipmentNumber", False) else "",
                    "diamond_shipment_id": result.get("shipmentId") if result.get("shipmentId", False) else "",
                }
                log_book.write(
                    {
                        "log_lines": [
                            (
                                0,
                                0,
                                {
                                    "message": response.text,
                                    "api_url": api_url,
                                    "api_data_sent": data_applied,
                                },
                            )
                        ]
                    }
                )

    def fetch_despatchlab_shipment(self):
        log_book = self.env["common.log.book.ept"].search([], limit=1)
        if not log_book:
            log_book = self.env["common.log.book.ept"].create({})
        token_url = "https://api.despatchlab.tech/v1/auth/token/credentials"
        header = {
            "Content-Type": "application/json",
        }
        data = {
            "key": f"{self.env.company.despatchlab_username}",
            "secret": f"{self.env.company.despatchlab_password}",
        }
        response = requests.post(token_url, data=json.dumps(data), headers=header)
        token = False
        if response.status_code in [200]:
            response_dict = json.loads(response.text)
            token = response_dict["tokens"]["access"]
        else:
            raise ValidationError(_("Failed to get token, authorization failed."))
        order_header = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token),
        }
        for order in self.filtered(lambda ord: ord.is_diamond_logistic_order_send):
            api_url = f"https://api.despatchlab.tech/v1/warehouse/orders/{order.diamond_logistic_order_id[1:-1]}"
            response = requests.get(api_url, data="", headers=order_header)
            result = json.loads(response.text)
            if response.status_code in [200]:
                diamond_warehouses = self.env["stock.warehouse"].search([("is_despatchlab_warehouse", "=", True)])
                for picking in order.picking_ids.filtered(
                    lambda pick: pick.state not in ["done", "cancel"]
                    and pick.location_id in diamond_warehouses.mapped("lot_stock_id")
                ):
                    if not bool(picking.carrier_tracking_ref):
                        picking.diamond_carrier = result.get("carrierName") if result.get("carrierName", False) else ""
                        picking.carrier_tracking_ref = (
                            result.get("shipmentNumber") if result.get("shipmentNumber", False) else ""
                        )
                        picking.diamond_shipment_id = (
                            result.get("shipmentId") if result.get("shipmentId", False) else ""
                        )
            data_applied = {
                "order": order.diamond_logistic_order_id,
                "diamond_carrier": result.get("carrierName") if result.get("carrierName", False) else "",
                "carrier_tracking_ref": result.get("shipmentNumber") if result.get("shipmentNumber", False) else "",
                "diamond_shipment_id": result.get("shipmentId") if result.get("shipmentId", False) else "",
            }
            log_book.write(
                {
                    "log_lines": [
                        (
                            0,
                            0,
                            {
                                "message": response.text,
                                "api_url": api_url,
                                "api_data_sent": data_applied,
                            },
                        )
                    ]
                }
            )

    def prepare_shopify_order_vals(
        self, instance, partner, shipping_address, invoice_address, order_response, payment_gateway, workflow
    ):
        res = super(SaleOrder, self).prepare_shopify_order_vals(
            instance, partner, shipping_address, invoice_address, order_response, payment_gateway, workflow
        )
        if res["shopify_instance_id"]:
            res["is_diamond_logistic_order"] = True
        return res
