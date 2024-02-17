from odoo import models, fields, api
import json
import requests
from odoo.exceptions import ValidationError


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("skynet", "Skynet")], ondelete={"skynet": "set default"})
    skynet_username = fields.Char("Username")
    skynet_password = fields.Char("Password")
    skynet_id = fields.Char("ID")
    skynet_pin = fields.Char("PIN")
    skynet_access_token = fields.Char("Skynet Access Token")
    skynet_sender_name = fields.Char("Name")
    skynet_sender_company_name = fields.Char("Company Name")
    skynet_sender_street = fields.Char("Street")
    skynet_sender_street2 = fields.Char("Street 2")
    skynet_sender_city = fields.Char("City")
    skynet_sender_zip = fields.Char("ZIP")
    skynet_sender_state_id = fields.Many2one("res.country.state", string="State")
    skynet_sender_country_id = fields.Many2one("res.country", string="Country")
    skynet_sender_phone = fields.Char("Phone")
    skynet_sender_email = fields.Char("Email")

    @api.model
    def skynet_send_shipping(self, pickings):
        for picking in pickings:
            try:
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
                    line.sale_line_id.name
                    # product_details.append({
                    #     "ItemAlt": "",
                    #     "ItemNoOfPcs":1,
                    #     "ItemCubicL": 0,
                    #     "ItemCubicW": 0,
                    #     "ItemCubicH": 0,
                    #     "ItemWeight": weight,
                    #     "ItemCubicWeight": 0,
                    #     "ItemDescription": line.description_picking,
                    #     "ItemCustomValue": product_value,
                    #     "ItemCustomCurrencyCode": product_currency,
                    #     "Notes": product_notes,
                    #     "Pieces":[]
                    # })

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
                picking.carrier_id.skynet_sender_city if picking.carrier_id.skynet_sender_city else picking.company_id.city
                sender_zip = (
                    picking.carrier_id.skynet_sender_zip
                    if picking.carrier_id.skynet_sender_zip
                    else picking.company_id.zip
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
                            "SenderAddCity": "",
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
                            "ReceiverName": picking.partner_id.parent_id.name,
                            "ReceiverCompanyName": picking.partner_id.name,
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
                            "GoodsDescription": "MARKETING SAMPLES",
                            "CustomValue": "",
                            "CustomCurrencyCode": product_value_currency,
                            "InsuranceValue": "",
                            "InsuranceCurrencyCode": "",
                            "ShipmentTerm": "",
                            "GoodsOriginCountryCode": picking.company_id.country_id.code,
                            "DeliveryInstructions": "",
                            "Weight": total_product_weight,
                            "WeightMeasurement": "KG",
                            "NoOfItems": int(picking.no_of_packages),
                            "CubicL": 0,
                            "CubicW": 0,
                            "CubicH": 0,
                            "CubicWeight": 0.0,
                            "ServiceTypeName": "SKYSAV",
                            "BookPickUP": False,
                            "AlternateRef": "",
                            "SenderRef1": picking.origin,
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
                api_url = f"{picking.carrier_id.company_id.skynet_api_url}/shipments"
                headers = {"Token": f"{picking.carrier_id.skynet_access_token}", "Content-Type": "application/json"}
                response = requests.post(api_url, data=json.dumps(data), headers=headers)
                if response.status_code == 200:
                    result = json.loads(response.text)
                    picking.carrier_tracking_ref = result[0]["ShipmentNumber"]
                    picking.skynet_label_url = result[0]["LabelURL"]
                    picking.skynet_error = False
                    return [{"tracking_number": result[0]["ShipmentNumber"], "exact_price": 0}]
                else:
                    picking.carrier_tracking_ref = False
                    picking.skynet_label_url = False
                    picking.skynet_error = response.text
                    return [{"error": response.text}]
            except Exception as e:
                raise ValidationError(e)
