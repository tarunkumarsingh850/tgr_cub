import requests
import json

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _description = "Stock Picking"

    diamond_carrier = fields.Char("Diamond Carrier")
    diamond_shipment_id = fields.Char("Diamond Logistic Order ID", copy=False)

    def send_diamond_shipment_cron(self):
        diamond_locations = (
            self.env["stock.warehouse"].search([("is_despatchlab_warehouse", "=", True)]).mapped("lot_stock_id").ids
        )
        diamond_transfers = self.env["stock.picking"].search(
            [
                ("payment_status", "in", ["paid", "credit"]),
                ("is_hold", "=", False),
                ("location_id", "in", diamond_locations),
                ("state", "in", ["confirmed", "assigned"]),
                ("carrier_tracking_ref", "=", False),
            ]
        )
        for transfer in diamond_transfers:
            order = self.env["sale.order"].search([("picking_ids", "in", transfer.ids)])
            if not order.is_diamond_logistic_order_send:
                token_url = "https://api.despatchlab.tech/v1/auth/token/credentials"
                header = {
                    "Content-Type": "application/json",
                }
                log_book = self.env["common.log.book.ept"].search([], limit=1)
                if not log_book:
                    log_book = self.env["common.log.book.ept"].create({})
                data = {
                    "key": f"{transfer.company_id.despatchlab_username}",
                    "secret": f"{transfer.company_id.despatchlab_password}",
                }
                response = requests.post(token_url, data=json.dumps(data), headers=header)
                token = False
                if response.status_code in [200]:
                    response_dict = json.loads(response.text)
                    token = response_dict["tokens"]["access"]
                else:
                    continue
                order_create_url = "https://api.despatchlab.tech/v1/warehouse/orders"
                order_create_header = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(token),
                }
                product_datas = []
                for line in transfer.move_ids_without_package.filtered(
                    lambda move_line: move_line.product_id.detailed_type == "product"
                ):
                    product_data = {"sku": line.product_id.default_code, "quantity": int(line.product_uom_qty)}
                    product_datas.append(product_data)
                diamond_data = {
                    "printDespatchNote": "true",
                    "addPackagingToOrder": "false",
                    # "address": 0,
                    "addressLine1": transfer.partner_id.street if transfer.partner_id.street else "",
                    "addressLine2": transfer.partner_id.street2 if transfer.partner_id.street2 else "",
                    "addressLine3": "",
                    "companyName": transfer.partner_id.name
                    if transfer.partner_id.name
                    else transfer.partner_id.parent_id.name,
                    # "countryId": transfer.partner_id.country_id.name if transfer.partner_id.country_id.name else "",
                    "countryId": 1,
                    "countyOrState": transfer.partner_id.state_id.name if transfer.partner_id.state_id.name else "",
                    "customerId": transfer.company_id.diamond_logistics_customer_id,
                    "customerReference": transfer.origin if transfer.origin else "",
                    "deliveryType": "Overnight",
                    "feature": "48 Hour",
                    # "latitude": 0,
                    "locationType": "Business",
                    # "longitude": 0,
                    "postcodeOrZip": transfer.partner_id.zip if transfer.partner_id.zip else "",
                    "postcodeSearch": transfer.partner_id.zip.lower() if transfer.partner_id.zip else "",
                    "products": product_datas,
                    "recipientEmail": transfer.partner_id.email,
                    "recipientName": transfer.partner_id.name,
                    "recipientNumber": "",
                    "serviceType": "48 Hour",
                    "townOrCity": transfer.partner_id.city if transfer.partner_id.city else "",
                }
                response = requests.post(order_create_url, data=json.dumps(diamond_data), headers=order_create_header)
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
                                    "api_data_sent": json.dumps(diamond_data),
                                },
                            )
                        ]
                    }
                )
