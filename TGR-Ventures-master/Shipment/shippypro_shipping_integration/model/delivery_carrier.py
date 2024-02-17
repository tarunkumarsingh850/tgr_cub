import binascii
from odoo.exceptions import ValidationError
from requests.auth import HTTPBasicAuth
from odoo import fields, models, _, api
import requests
import json
import time
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("shippypro", "Shippypro")], ondelete={"shippypro": "set default"})

    shippypro_shipping_service = fields.Selection(
        [("express", "Express"), ("Standard", "standard")], string="Shippypro Shipping Service"
    )
    shippypro_payment_method = fields.Selection(
        [("Paypal", "Paypal"), ("COD", "COD")], string="Shippypro Payment Method"
    )
    shippypro_package_id = fields.Many2one("product.packaging", string="Default Package")

    shippypro_carrier_id = fields.Many2one("shippypro.carrier", string="Shippypro Carrie")

    def shippypro_rate_shipment(self, order):
        request_data = self.shippypro_rate_request_data(order)
        url = self.company_id and self.company_id.shippypro_api_url
        headers = {"Content-Type": "application/json"}
        username = self.company_id and self.company_id.shippypro_api_key
        try:
            _logger.info(">>> sending data to {} \n request data:- {}".format(url, request_data))
            response_data = requests.post(
                url=url, auth=HTTPBasicAuth(username=username, password=""), data=request_data, headers=headers
            )
            shippypro_service_rate_obj = self.env["shippypro.service.rate"]
            if response_data.status_code in [200, 201]:
                _logger.info(">>> get successfully response from SHIP RATE API")
                response_data = response_data.json()
                rates = response_data.get("Rates")
                if not rates:
                    raise ValidationError(_("Rate not found in response \n {}".format(response_data)))
                existing_record = shippypro_service_rate_obj.sudo().search([("sale_id", "=", order.id)])
                existing_record.unlink()
                _logger.info("Rate Response %s" % rates)
                _logger.info(order.carrier_id)
                for rate in rates:
                    vals = {
                        "carrier_name": rate.get("carrier"),
                        "carrier_id": rate.get("carrier_id"),
                        "carrier_label": rate.get("carrier_label"),
                        "carrier_rate": float(rate.get("rate")),
                        "carrier_rate_id": rate.get("rate_id"),
                        "delivery_day": rate.get("delivery_days"),
                        "service": rate.get("service"),
                        "sale_id": order.id,
                        "order_id": rate.get("order_id"),
                    }
                    shippypro_service_rate_obj.sudo().create(vals)
                shippypro_service_id = 0
                if order.carrier_id:
                    shippypro_service_id = (
                        self.env["shippypro.service.rate"]
                        .sudo()
                        .search(
                            [
                                ("carrier_id", "=", order.carrier_id.shippypro_carrier_id.carrier_id),
                                ("sale_id", "=", order.id),
                            ],
                            limit=1,
                        )
                    )
                _logger.info("Rate Response %s" % shippypro_service_id)
                if not shippypro_service_id:
                    raise ValidationError(
                        _("%s Service rate not found from sender address to receiver address")
                        % (self.shippypro_carrier_id.carrier_label)
                    )
                order.shippypro_service_id = shippypro_service_id and shippypro_service_id.id
                return {
                    "success": True,
                    "price": shippypro_service_id and shippypro_service_id.carrier_rate or 0.0,
                    "error_message": False,
                    "warning_message": False,
                }
            else:
                raise ValidationError(response_data.content)
        except Exception as error:
            raise ValidationError(error)

    def shippypro_rate_request_data(self, order):
        """
        :returns this method return request data of rate api
        """
        sender_id = order and order.partner_id
        receiver_id = order and order.company_id

        request_data = {
            "Method": "GetRates",
            "Params": {
                "to_address": {
                    "name": receiver_id.name,
                    "company": receiver_id.name,
                    "street1": receiver_id.street,
                    "street2": receiver_id.street2 or " ",
                    "city": receiver_id.city,
                    "state": receiver_id and receiver_id.state_id and receiver_id.state_id.code or " ",
                    "zip": receiver_id.zip,
                    "country": receiver_id and receiver_id.country_id and receiver_id.country_id.code or " ",
                    "phone": receiver_id.phone or " ",
                    "email": receiver_id.email or " ",
                },
                "from_address": {
                    "name": sender_id.name,
                    "company": sender_id.name,
                    "street1": sender_id.street,
                    "street2": sender_id.street2 or " ",
                    "city": sender_id.city,
                    "state": sender_id and sender_id.state_id and sender_id.state_id.code or " ",
                    "zip": sender_id.zip,
                    "country": sender_id and sender_id.country_id and sender_id.country_id.code or " ",
                    "phone": sender_id.phone or " ",
                    "email": sender_id.email or " ",
                },
                "parcels": [
                    {
                        "length": 10,
                        "width": 10,
                        "height": 10,
                        "weight": 10,
                    }
                ],
                "Insurance": 0,
                "Async": False,
                "InsuranceCurrency": self.company_id.currency_id.name,
                "CashOnDelivery": 0,
                "CashOnDeliveryCurrency": self.company_id
                and self.company_id.currency_id
                and self.company_id.currency_id.name,
                "ContentDescription": "Shoes",
                "TotalValue": "{} {}".format(order.amount_total, self.company_id.currency_id.name),
                "ShippingService": "{}".format(self.shippypro_shipping_service),
            },
        }
        return json.dumps(request_data)

    def shippypro_ship_api_request_data(self, pickings):
        """
        :returns this method return request data for ship api
        """

        sender_id = self.company_id
        receiver_id = pickings.partner_id
        # shippypro_service_id = pickings.sale_id and pickings.sale_id.shippypro_service_id
        # carrier_name = (
        #     shippypro_service_id
        #     and shippypro_service_id.carrier_name
        #     or self.shippypro_carrier_id
        #     and self.shippypro_carrier_id.name
        # )
        # carrier_service = (
        #     shippypro_service_id
        #     and shippypro_service_id.service
        #     or self.shippypro_carrier_id
        #     and self.shippypro_carrier_id.carrier_service
        # )
        # carrier_id = (
        #     shippypro_service_id
        #     and shippypro_service_id.carrier_id
        #     or self.shippypro_carrier_id
        #     and self.shippypro_carrier_id.carrier_id
        # )
        request_data = {
            "Method": "Ship",
            "Params": {
                "to_address": {
                    "name": str(receiver_id.name) if receiver_id else "--",
                    "company": str(receiver_id.name) if receiver_id else "--",
                    "street1": str(receiver_id.street) if receiver_id.street else "--",
                    "street2": receiver_id.street2 if receiver_id.street2 else "--",
                    "city": str(receiver_id.city) if receiver_id.city else "--",
                    "state": "",
                    "zip": str(receiver_id.zip) if receiver_id.zip else "--",
                    "country": str(receiver_id.country_id.code) if receiver_id.country_id else "--",
                    "phone": str(receiver_id.phone) or " ",
                    "email": str(receiver_id.email) or " ",
                },
                "from_address": {
                    "name": str(self.env.user.name) or "--",
                    "company": str(sender_id.name),
                    "street1": str(sender_id.street) if sender_id.street else "--",
                    "street2": sender_id.street2 if sender_id.street2 else "--",
                    "city": str(sender_id.city) if sender_id.city else "--",
                    "state": "",
                    "zip": str(sender_id.zip) if sender_id else "--",
                    "country": str(sender_id.country_id.code) if sender_id.country_id.code else "--",
                    "phone": str(sender_id.phone) if sender_id.phone else "--",
                    "email": str(sender_id.email) if sender_id.email else "--",
                },
                "parcels": [
                    {
                        "length": int(pickings.parcel_length) if pickings.parcel_length else int(5),
                        "width": int(pickings.parcel_width) if pickings.parcel_width else int(5),
                        "height": int(pickings.parcel_height) if pickings.parcel_height else int(5),
                        "weight": int(pickings.parcel_weight) if pickings.parcel_weight else int(1),
                    }
                ],
                "TotalValue": str("{} {}".format(pickings.sale_id.amount_total, self.company_id.currency_id.name)),
                "TransactionID": str(pickings.sale_id.name) if pickings.sale_id else "--",
                "ContentDescription": str(pickings.origin),
                "Insurance": 0,
                "CashOnDelivery": 0,
                "CashOnDeliveryType": 0,
                "CarrierName": str(self.shippypro_carrier_id.name),
                "CarrierService": str(self.shippypro_carrier_id.carrier_service),
                "CarrierID": int(str(self.shippypro_carrier_id.carrier_id)),
                "OrderID": "",
                "RateID": "",
                "BillAccountNumber": "",
            },
        }
        return json.dumps(request_data)

    @api.model
    def shippypro_send_shipping(self, pickings):
        request_data = self.shippypro_ship_api_request_data(pickings)
        headers = {"Content-Type": "application/json"}
        username = self.company_id and self.company_id.shippypro_api_key
        try:
            response_data = requests.post(
                url=self.company_id and self.company_id.shippypro_api_url,
                auth=HTTPBasicAuth(username=username, password=""),
                headers=headers,
                data=request_data,
            )
            if response_data.status_code in [200, 201]:
                response_data = response_data.json()
                order_id = response_data.get("NewOrderID")
                pickings.shippypro_order_id = order_id
                if not order_id:
                    raise ValidationError(_("order id not found in response {}").format(response_data))
                time.sleep(10)  # Sleep for 3 seconds
                label_response = self.generate_label_using_order_id(order_id)
                label_data = label_response and label_response.get("PDF")
                if label_data:
                    for data in label_data:
                        data = binascii.a2b_base64(str(data))
                        message = ("Label created!<br/> <b>Order  Number : </b>%s<br/>") % (order_id,)
                        pickings.message_post(body=message, attachments=[("Shippypro-{}.{}".format(order_id, "pdf"), data)])
                tracking_number = label_response.get("TrackingNumber")
                tracking_url = label_response.get("TrackingExternalLink")
                pickings.shippypro_tracking_url = tracking_url
                shipping_data = {"exact_price": float(0.0), "tracking_number": tracking_number}
                shipping_data = [shipping_data]
                return shipping_data
            else:
                raise ValidationError(_(response_data.content))
        except Exception as error:
            raise ValidationError(_(error))

    def generate_label_using_order_id(self, order_id):
        request_data = {"Method": "GetLabelUrl", "Params": {"OrderID": int(order_id), "LabelType": "PDF"}}
        headers = {"Content-Type": "application/json"}
        username = self.company_id and self.company_id.shippypro_api_key
        _logger.info(request_data)
        url = self.company_id and self.company_id.shippypro_api_url
        _logger.info(username, "url", url)

        try:
            response_data = requests.post(
                url=self.company_id and self.company_id.shippypro_api_url,
                headers=headers,
                auth=HTTPBasicAuth(username=username, password=""),
                data=json.dumps(request_data),
            )

            if response_data.status_code in [200, 201]:
                response_data = response_data.json()
                _logger.info(">>> get successfully label data %s", response_data)
                return response_data
            else:
                raise ValidationError(response_data)
        except Exception as error:
            raise ValidationError(error)

    def shippypro_cancel_shipment(self, picking):
        data = {"Method": "ArchiveOrders", "Params": {"OrderIDS": [int(picking.shippypro_order_id)]}}
        headers = {"Content-Type": "application/json"}
        username = self.company_id and self.company_id.shippypro_api_key
        try:
            _logger.info("Sending data for cancel the order {}".format(data))
            response_data = requests.post(
                url=self.company_id and self.company_id.shippypro_api_url,
                headers=headers,
                auth=HTTPBasicAuth(username=username, password=""),
                data=json.dumps(data),
            )
            if response_data.status_code in [200, 201]:
                _logger.info("Get successfully response of cancel api")
                response_data = response_data.json()
                result = response_data and response_data.get("Result")
                if result in ["OK", "ok"]:
                    _logger.info("Successfully cancel order {}".format(picking.shippypro_order_id))
                else:
                    raise ValidationError(_("get some error to cancel the  order \n").format(response_data))
            else:
                raise ValidationError(_("get some error to cancel the  order \n {}").format(response_data.text))
        except Exception as error:
            raise ValidationError(_(error))

    def shippypro_get_tracking_link(self, pickings):
        if pickings.shippypro_tracking_url:
            return pickings.shippypro_tracking_url
