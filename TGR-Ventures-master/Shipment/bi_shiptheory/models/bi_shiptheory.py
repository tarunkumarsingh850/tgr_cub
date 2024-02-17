from odoo.exceptions import ValidationError
from odoo import models
import requests
import logging
from odoo import _, fields, models
import binascii
import base64
import json


_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[("shiptheory", "Ship Theory")],
        ondelete={"shiptheory": "set default"},
    )
    shiptheory_email = fields.Char(string="Shiptheory Email")
    shiptheory_password = fields.Char(string="Shiptheroy Password")
    delivery_service = fields.Char(string="Delivery Service ID")
    delivery_increment = fields.Char(string="Delivery Increment No.")
    enhancement_id = fields.Char(string="Delivery Service Enhancement ID")
    format_id = fields.Char(string="Delivery Service Format ID")
    is_uk_address = fields.Boolean(string="Is UK Address", copy=False)

    def shiptheory_send_shipping(self, pickings):
        request_data = self.shiptheory_ship_api_request_data(pickings)
        username = self.shiptheory_email
        password = self.shiptheory_password
        token_api_url = "https://api.shiptheory.com/v1/token"
        params = {"email": username, "password": password}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        try:
            response_data = requests.post(
                url=token_api_url,
                headers=headers,
                json=params,
            )
            if response_data.status_code in [200, 201]:
                response_data = response_data.json()
                data = response_data.get("data")
                if not data:
                    raise ValidationError(
                        _("Token not generated,Invalid Credentials in response {}").format(response_data)
                    )
                else:
                    token_generated = data["token"]
                    # self.shiptheory_ship_api_request_data(pickings, token_generated)
                    shipment_url = "https://api.shiptheory.com/v1/shipments"
                    shipment_headers = {
                        "Content-type": "application/json",
                        "Accept": "application/json",
                        "Authorization": "Bearer {}".format(token_generated),
                        "Content-Length": str(2),
                    }
                    try:
                        res = requests.post(shipment_url, data=json.dumps(request_data), headers=shipment_headers)
                        if res.status_code in [200, 201]:
                            response_data = res.json()
                            if "error" in response_data.keys():
                                msg = response_data.get("error")
                                raise ValidationError(_(msg))
                            carrier_result = response_data.get("carrier_result")
                            tracking = carrier_result.get("tracking")
                            pickings.carrier_tracking_ref = tracking
                            pickings.shiptheory_tracking = token_generated
                            ref = pickings.origin
                            label_response = self.generate_shiptheory_label_using_order_id(
                                pickings, ref, token_generated
                            )
                            label_data = label_response and label_response.get("PDF")
                            if label_data:
                                for data in label_data:
                                    data = binascii.a2b_base64(str(data))
                                    message = ("Label created!<br/> <b>Order  Number : </b>%s<br/>") % (ref,)
                                    pickings.message_post(
                                        body=message, attachments=[("Shiptheory-{}.{}".format(ref, "pdf"), data)]
                                    )
                            tracking_number = label_response.get("TrackingNumber")
                            shipping_data = {"exact_price": float(0.0), "tracking_number": tracking_number}
                            shipping_data = [shipping_data]
                            return shipping_data
                        else:
                            raise ValidationError(_(response_data.content))
                    except Exception as error:
                        raise ValidationError(_(error))
            else:
                raise ValidationError(_(response_data.content))
        except Exception as error:
            raise ValidationError(_(error))

    def shiptheory_ship_api_request_data(self, pickings):
        """
        :returns this method return request data for ship api
        """

        sender_id = pickings.company_id
        if pickings.carrier_id.is_uk_address:
            sender_company = pickings.company_id.name if pickings.company_id.name else "N/A"
            sender_firstname = pickings.company_id.name if pickings.company_id.name else "N/A"
            sender_lastname = "1"
            sender_address_line_1 = pickings.company_id.uk_street if pickings.company_id.uk_street else "N/A"
            sender_city = pickings.company_id.uk_city if pickings.company_id.uk_city else "N/A"
            sender_postcode = pickings.company_id.uk_zip if pickings.company_id.uk_zip else "N/A"
            sender_telephone = pickings.company_id.uk_phone if pickings.company_id.uk_phone else "N/A"
            sender_country = pickings.company_id.uk_country_id.code if pickings.company_id.uk_country_id.code else "N/A"
            sender_email = pickings.company_id.uk_email if pickings.company_id.uk_email else "N/A"
        else:
            sender_company = sender_id.company_id.name if sender_id.company_id.name else "N/A"
            sender_firstname = sender_id.company_id.name if sender_id.company_id.name else "N/A"
            sender_lastname = "1"
            sender_address_line_1 = sender_id.company_id.street if sender_id.company_id.street else "N/A"
            sender_city = sender_id.company_id.city if sender_id.company_id.city else "N/A"
            sender_postcode = sender_id.company_id.zip if sender_id.company_id.zip else "N/A"
            sender_telephone = sender_id.company_id.phone if sender_id.company_id.phone else "N/A"
            sender_country = sender_id.company_id.country_id.code if sender_id.company_id.country_id.code else "N/A"
            sender_email = sender_id.company_id.email if sender_id.company_id.email else "N/A"

        receiver_id = pickings.partner_id
        pickings.shiptheory_scheduled_date.date()
        if pickings.weight:
            pickings.weight
        elif pickings.shipping_weight:
            pickings.shipping_weight
        else:
            pass
        items = []
        for line in pickings.move_ids_without_package:
            items.append(
                {
                    "name": line.product_id.name,
                    "sku": line.product_id.default_code,
                    "qty": line.quantity_done,
                    "value": 32.50,
                    "weight": 0.5,
                }
            )
        # receiver_id.street if receiver_id.street else "N/A"
        street = receiver_id.street if receiver_id.street else " "
        street2 = receiver_id.street2 if receiver_id.street2 else " "
        state = receiver_id.state_id.name if receiver_id.state_id else " "
        receiver_address = street + "," + street2 + "," + state
        request_data = {
            "reference": pickings.origin,
            "reference2": pickings.origin,
            "delivery_service": self.delivery_service if self.delivery_service else "",
            "increment": self.delivery_increment if self.delivery_increment else "",
            "shipment_detail": {
                "weight": 0.5,
                "parcels": 1,
                "value": 0,
                "enhancement_id": self.enhancement_id if self.enhancement_id else "N/A",
                "format_id": self.format_id if self.format_id else "N/A",
                "shipping_price": 3.99,
                "reference3": pickings.name,
                "sales_source": "ODOO",
                # "ship_date": str(picking_date),
                "rules_metadata": "custom string",
                "duty_tax_number": pickings.company_id.vat if pickings.company_id.vat else "N/A",
                "duty_tax_number_type": "IOSS",
            },
            "recipient": {
                "company": receiver_id.company_id.name if receiver_id.company_id.name else "N/A",
                "firstname": receiver_id.name if receiver_id.name else "N/A",
                "lastname": "1",
                "address_line_1": receiver_address if receiver_address else "N/A",
                "city": receiver_id.city if receiver_id.city else "N/A",
                "postcode": receiver_id.zip if receiver_id.zip else "N/A",
                "telephone": receiver_id.phone if receiver_id.phone else "N/A",
                "country": receiver_id.country_id.code if receiver_id.country_id.code else "N/A",
                "tax_number": receiver_id.vat if receiver_id.vat else "N/A",
            },
            "sender": {
                "company": sender_company,
                "firstname": sender_firstname,
                "lastname": sender_lastname,
                "address_line_1": sender_address_line_1,
                "city": sender_city,
                "postcode": sender_postcode,
                "telephone": sender_telephone,
                "country": sender_country,
                "email": sender_email,
            },
            "products": items,
            "packages": [{"id": 0, "weight": 0}],
        }
        return request_data

    def generate_shiptheory_label_using_order_id(self, pickings, ref, token_generated):
        view_shipment_url = "https://api.shiptheory.com/v1/shipments/"
        api_url = "{}{}".format(view_shipment_url, ref)
        param = {}
        new_headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer {}".format(token_generated),
        }
        label_response = requests.get(api_url, json=param, headers=new_headers)
        label_response = label_response.json()
        label_data = label_response.get("label")
        # label_data = label_response and label_response.get("label")
        if label_data:
            # Decode base64 String Data
            decodedData = base64.b64decode(label_data)
            # Write PDF from Base64 File
            # pdfFile = open('sample.pdf', 'wb')
            # pdfFile.write(decodedData)
            # pdfFile.close()
            # data = binascii.a2b_base64(str(label_data))
            message = ("Label created!<br/> <b>Order  Number : </b>%s<br/>") % (ref,)
            pickings.message_post(body=message, attachments=[("Shiptheory-{}.{}".format(ref, "pdf"), decodedData)])

        return label_response
