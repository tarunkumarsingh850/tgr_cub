import json
import requests

from odoo import models, fields, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _description = "Stock Picking"

    skynet_label_url = fields.Char("Skynet Label URL")
    skynet_error = fields.Text("Skynet Error")

    def send_to_skynet(self):
        for picking in self:
            product_details = []
            total_product_value = 0
            product_value_currency = False
            total_product_weight = 0
            for line in picking.move_ids_without_package:
                weight = 0
                if line.product_id.weight:
                    weight = line.product_id.weight * line.product_uom_qty
                total_product_weight += weight
                product_value = line.sale_line_id.price_subtotal
                total_product_value += product_value
                product_currency = line.sale_line_id.order_id.currency_id.name
                product_value_currency = product_currency
                product_notes = line.sale_line_id.name
                product_details.append(
                    {
                        "ItemAlt": "",
                        "ItemNoOfPcs": 1,
                        "ItemCubicL": 0,
                        "ItemCubicW": 0,
                        "ItemCubicH": 0,
                        "ItemWeight": weight,
                        "ItemCubicWeight": 0,
                        "ItemDescription": line.description_picking,
                        "ItemCustomValue": product_value,
                        "ItemCustomCurrencyCode": product_currency,
                        "Notes": product_notes,
                        "Pieces": [],
                    }
                )

            sender_name = (
                picking.carrier_id.skynet_sender_name
                if picking.carrier_id.skynet_sender_name
                else picking.company_id.name
            )
            sender_company_name = (
                picking.carrier_id.skynet_sender_company_name
                if picking.carrier_id.skynet_sender_company_name
                else picking.company_id.name
            )
            sender_street = (
                picking.carrier_id.skynet_sender_street
                if picking.carrier_id.skynet_sender_street
                else picking.company_id.street
            )
            sender_street2 = (
                picking.carrier_id.skynet_sender_street2
                if picking.carrier_id.skynet_sender_street2
                else picking.company_id.street2
            )
            sender_city = (
                picking.carrier_id.skynet_sender_city
                if picking.carrier_id.skynet_sender_city
                else picking.company_id.city
            )
            sender_zip = (
                picking.carrier_id.skynet_sender_zip if picking.carrier_id.skynet_sender_zip else picking.company_id.zip
            )
            sender_state = (
                picking.carrier_id.skynet_sender_state_id
                if picking.carrier_id.skynet_sender_state_id
                else picking.company_id.state_id
            )
            sender_country = (
                picking.carrier_id.skynet_sender_country_id
                if picking.carrier_id.skynet_sender_country_id
                else picking.company_id.country_id
            )
            sender_phone = (
                picking.carrier_id.skynet_sender_phone
                if picking.carrier_id.skynet_sender_phone
                else picking.company_id.phone
            )
            sender_email = (
                picking.carrier_id.skynet_sender_email
                if picking.carrier_id.skynet_sender_email
                else picking.company_id.email
            )
            data = [
                {
                    "ThirdPartyToken": "",
                    "SenderDetails": {
                        "SenderName": sender_name,
                        "SenderCompanyName": sender_company_name,
                        "SenderCountryCode": sender_country.code if sender_country else "",
                        "SenderAdd1": sender_street,
                        "SenderAdd2": sender_street2,
                        "SenderAdd3": "",
                        "SenderAddCity": sender_city,
                        "SenderAddState": sender_state.name if sender_state else "",
                        "SenderAddPostcode": sender_zip,
                        "SenderPhone": sender_phone,
                        "SenderEmail": "shipping@tiger-one.eu",
                        "SenderFax": "",
                        "SenderKycType": "",
                        "SenderKycNumber": "",
                        "SenderReceivingCountryTaxID": "",
                    },
                    "ReceiverDetails": {
                        "ReceiverName": picking.partner_id.name,
                        "ReceiverCompanyName": picking.partner_id.parent_id.name,
                        "ReceiverCountryCode": picking.partner_id.country_id.code,
                        "ReceiverAdd1": picking.partner_id.street,
                        "ReceiverAdd2": picking.partner_id.street2,
                        "ReceiverAdd3": "",
                        "ReceiverAddCity": picking.partner_id.city,
                        "ReceiverAddState": picking.partner_id.state_id.name if picking.partner_id.state_id else "",
                        "ReceiverAddPostcode": picking.partner_id.zip,
                        "ReceiverMobile": picking.partner_id.mobile,
                        "ReceiverPhone": picking.partner_id.phone,
                        "ReceiverEmail": picking.partner_id.email,
                        "ReceiverAddResidential": "",
                        "ReceiverFax": "",
                        "ReceiverKycType": "",
                        "ReceiverKycNumber": "",
                    },
                    "PackageDetails": {
                        "GoodsDescription": picking.note,
                        "CustomValue": total_product_value,
                        "CustomCurrencyCode": product_value_currency,
                        "InsuranceValue": "",
                        "InsuranceCurrencyCode": "",
                        "ShipmentTerm": "",
                        "GoodsOriginCountryCode": picking.company_id.country_id.code,
                        "DeliveryInstructions": "",
                        "Weight": total_product_weight,
                        "WeightMeasurement": "KG",
                        "NoOfItems": 1,
                        "CubicL": 0,
                        "CubicW": 0,
                        "CubicH": 0,
                        "CubicWeight": 0.0,
                        "ServiceTypeName": "EN",
                        "BookPickUP": False,
                        "AlternateRef": "",
                        "SenderRef1": "",
                        "SenderRef2": "",
                        "SenderRef3": "",
                        "DeliveryAgentCode": "",
                        "DeliveryRouteCode": "",
                        "ShipmentResponseItem": product_details,
                        "CODAmount": 0.0,
                        "CODCurrencyCode": "",
                        "Bag": 0,
                        "Notes": picking.note,
                        "OriginLocCode": "",
                        "BagNumber": 0,
                        "DeadWeight": total_product_weight,
                        "ReasonExport": "",
                        "DestTaxes": 0.0,
                        "Security": 0.0,
                        "Surcharge": 0.0,
                        "ReceiverTaxID": "",
                        "OrderNumber": "",
                        "Incoterms": "CIF",
                        "ClearanceReference": "",
                    },
                    "PickupDetails": {
                        "ReadyTime": "",
                        "CloseTime": "",
                        "SpecialInstructions": "",
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "AddressState": "",
                        "AddressCity": "",
                        "AddressPostalCode": "",
                        "AddressCountryCode": "",
                    },
                }
            ]
            api_url = f"{picking.carrier_id.company_id.skynet_api_url}/shipment"
            headers = {"Token": "D3C49BD7449BF4304F5557D610621812", "Content-Type": "application/json"}
            response = requests.post(api_url, data=json.loads(data), headers=headers)
            if response.code == 200:
                result = json.loads(response.text)
                picking.carrier_tracking_ref = result["ShipmentNumber"]
                picking.skynet_label_url = result["LabelURL"]
                picking.skynet_error = False
            else:
                picking.carrier_tracking_ref = False
                picking.skynet_label_url = False
                picking.skynet_error = response.text

    # def button_validate(self):
    #     result = super(StockPicking, self).button_validate()
    #     if self.env.context.get('skip_immediate', False):
    #         for picking in self:
    #             picking.send_to_skynet()
    #     return result

    def retry_skynet(self):
        for picking in self:
            if picking.carrier_id.delivery_type != "skynet":
                raise UserError(_("This is not a Skynet delivery."))
            picking.send_to_skynet()
