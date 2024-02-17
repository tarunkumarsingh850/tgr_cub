from odoo.exceptions import ValidationError
from requests.auth import HTTPBasicAuth
from odoo import models
import requests
import logging

_logger = logging.getLogger(__name__)


class ResCompanyDelivery(models.Model):
    _inherit = "delivery.carrier"

    def despatch_shipment(self, order):
        request_data = self.despatch_shipment_sample_data(order)
        url = self.company_id and self.company_id.despatch_api_url
        headers = {"Content-Type": "application/json"}
        username = self.company_id and self.company_id.despatch_api_key
        password = self.company_id.despatch_api_secret
        try:
            _logger.info(">>> sending data to {} \n request data:- {}".format(url, request_data))
            response_data = requests.post(
                url=url, auth=HTTPBasicAuth(username=username, password=password), data=request_data, headers=headers
            )
        except Exception as error:
            raise ValidationError(error)

    def despatch_shipment_sample_data(self, order):
        receiver_id = order and order.company_id
        {
            "pickUpDate": "2018-08-01",
            "recipient": {
                "name": str(receiver_id.name) if receiver_id else "--",
                "email": str(receiver_id.email) or " ",
                "phone": str(receiver_id.phone) or " ",
                "address": {
                    "companyName": str(receiver_id.name) if receiver_id.company_id else "--",
                    "addressLine1": str(receiver_id.street) if receiver_id.street else "--",
                    "addressLine2": receiver_id.street2 if receiver_id.street2 else "--",
                    "addressLine3": "--",
                    "townOrCity": str(receiver_id.city) if receiver_id.city else "--",
                    "countyOrState": str(receiver_id.country_id.name) if receiver_id.country_id else "--",
                    "postcodeOrZip": str(receiver_id.zip) if receiver_id.zip else "--",
                    "countryCode": str(receiver_id.country_id.code) if receiver_id.country_id else "--",
                },
            },
            "packages": [{"qty": "", "weightKg": "", "lengthCm": "", "heightCm": "", "depthCm": ""}],
            "service": {"carrier": "", "service": "Next Day", "feature": ""},
            "refs": {"senderRef": "Your ref", "recipientRef": "Your customer's ref"},
            "instructions": {
                "flags": ["Hazardous", "Fragile", "Liquid", "Secure", "SignatureRequired"],
                "goodsDescription": "",
                "notes": "",
                "liabilityCoverAmount": "50.00",
                "declaredValue": "20.00",
                "countryOfOriginCode": "",
                "customsCategory": "",
                "internatinalExportType": "",
                "harmonisedCodes": ["0102211000"],
            },
            "actions": {"printToGoogleCloudPrinter": False, "waitForLabel": True},
        }
