import pytz
from datetime import datetime
import requests
from odoo import models, fields, api, _
import logging
import xml.etree.ElementTree as etree
from odoo.exceptions import ValidationError
from odoo.addons.stamps_shipping_integration.models.stamps_response import Response
from unicodedata import normalize

_logger = logging.getLogger("Stamps.com")


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("stamps", "Stamps.com")], ondelete={"stamps": "set default"})

    stamps_packaging_id = fields.Many2one("stock.package.type", string="Default Package Type")

    stamps_package_type = fields.Selection(
        [
            ("Postcard", "Postcard"),
            ("Letter", "Letter"),
            ("Flat", "Flat"),
            ("Package", "Package"),
            ("Thick Envelope", "Thick Envelope"),
            ("Package", "Package"),
            ("Small Flat Rate Box", "Small Flat Rate Box"),
            ("Flat Rate Box", "Flat Rate Box"),
            ("Large Flat Rate Box", "Large Flat Rate Box"),
            ("Flat Rate Envelope", "Flat Rate Envelope"),
            ("Flat Rate Padded Envelope", "Flat Rate Padded Envelope"),
            ("Large Package", "Large Package"),
            ("Oversized Package", "Oversized Package"),
            ("Regional Rate Box A", "Regional Rate Box A"),
            ("Regional Rate Box B", "Regional Rate Box B"),
            ("Regional Rate Box C", "Regional Rate Box C"),
            ("Legal Flat Rate Envelope", "Legal Flat Rate Envelope"),
        ],
        string="Stamps.com Package Type",
        help="Stamps.com provide the package",
    )

    stam_service_info = fields.Selection(
        [
            ("US-FC", "US-FC"),
            ("US-MM", "US-MM"),
            ("US-PP", "US-PP"),
            ("US-PM", "US-PM"),
            ("US-XM", "US-XM"),
            ("US-EMI", "US-EMI"),
            ("US-PMI", "US-PMI"),
            ("US-FCI", "US-FCI"),
            ("US-LM", "US-LM"),
            ("US-CM", "US-CM"),
            ("US-PS", "US-PS"),
            ("US-LM", "US-LM"),
            ("DHL-PE", "DHL-PE"),
            ("DHL-PG", "DHL-PG"),
            ("DHL-PPE", "DHL-PPE"),
            ("DHL-PPG", "DHL-PPG"),
            ("DHL-BPME", "DHL-BPME"),
            ("DHL-BPMG", "DHL-BPMG"),
            ("DHL-MPE", "DHL-MPE"),
            ("DHL-MPG", "DHL-MPG"),
        ],
        string="Stamps.com Service Type",
        help="Stamps.com provide the package",
    )

    company_name = fields.Char(string="Company Name")
    po_box = fields.Char(string="PO BOX")
    city = fields.Char(string="City")
    state = fields.Char(string="State")
    zip_code = fields.Char(string="Zip Code")
    country = fields.Char(string="Country")

    def stamps_rate_shipment(self, orders):
        for order in orders:
            order_lines_without_weight = order.order_line.filtered(
                lambda line_item: not line_item.product_id.type in ["service", "digital"]
                and not line_item.product_id.weight
                and not line_item.is_delivery
            )
            for order_line in order_lines_without_weight:
                return {
                    "success": False,
                    "price": 0.0,
                    "error_message": "Please define weight in product : \n %s" % (order_line.product_id.name),
                    "warning_message": False,
                }

            # Shipper and Recipient Address
            sender_id = order.warehouse_id.partner_id
            receiver_id = order.partner_shipping_id

            # check sender Address
            if not sender_id.zip or not sender_id.city or not sender_id.country_id:
                return {
                    "success": False,
                    "price": 0.0,
                    "error_message": "Please Define Proper Sender Address!",
                    "warning_message": False,
                }

            # check Receiver Address
            if not receiver_id.zip or not receiver_id.city or not receiver_id.country_id:
                return {
                    "success": False,
                    "price": 0.0,
                    "error_message": "Please Define Proper Recipient Address!",
                    "warning_message": False,
                }

            total_weight = sum((line.product_id.weight * line.product_uom_qty) for line in order.order_line) or 0.0

            pound_for_kg = 35.274
            uom_id = self.env["product.template"]._get_weight_uom_id_from_ir_config_parameter()
            if uom_id.name == "lb":
                round(total_weight, 3)
            else:
                round(total_weight * pound_for_kg, 3)

            # pound_for_kg = 2.20462
            # ounce_for_kg = 35.274
            # WeightLb = round(total_weight * pound_for_kg, 3)
            # WeightOz = round(total_weight * ounce_for_kg, 3)

            master_node = etree.Element("Envelope")
            master_node.attrib["xmlns"] = "http://schemas.xmlsoap.org/soap/envelope/"

            submater_node = etree.SubElement(master_node, "Body")
            root_node = etree.SubElement(submater_node, "GetRates")
            root_node.attrib["xmlns"] = "http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111"
            # etree.SubElement(root_node, "Authenticator").text = self.company_id and self.company_id.stamps_authenticator

            shipment_data = etree.SubElement(root_node, "Credentials")

            etree.SubElement(shipment_data, "IntegrationID").text = "%s" % (
                self.company_id and self.company_id.stamps_integrator_id
            )
            etree.SubElement(shipment_data, "Username").text = "%s" % (
                self.company_id and self.company_id.stamps_user_name
            )
            etree.SubElement(shipment_data, "Password").text = "%s" % (
                self.company_id and self.company_id.stamps_password
            )

            shipment_data = etree.SubElement(root_node, "Rate")
            from_tag = etree.SubElement(shipment_data, "From")
            etree.SubElement(from_tag, "State").text = "%s" % (sender_id.state_id.code)
            etree.SubElement(from_tag, "ZIPCode").text = "%s" % (sender_id.zip)
            etree.SubElement(from_tag, "Country").text = "%s" % (sender_id.country_id.code)

            to_tag = etree.SubElement(shipment_data, "To")
            etree.SubElement(to_tag, "Country").text = "%s" % (receiver_id.country_id.code)
            # etree.SubElement(shipment_data, "WeightOz").text = "%s" % (weight_lb)
            etree.SubElement(shipment_data, "WeightLb").text = "%s" % (0.3125)
            etree.SubElement(shipment_data, "PackageType").text = "%s" % (self.stamps_package_type)

            current_date = datetime.strftime(datetime.now(pytz.utc), "%Y-%m-%d")  # '2020-10-01'
            etree.SubElement(shipment_data, "ShipDate").text = current_date
            etree.SubElement(root_node, "Carrier")
            request_data = etree.tostring(master_node)
            url = "%s" % (self.company_id.stamps_api_url)
            stamp_shipping_charge_obj = self.env["stamp.shipping.charge"]
            headers = {
                "SOAPAction": "http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111/GetRates",
                "Content-Type": 'text/xml; charset="utf-8"',
            }
            try:
                _logger.info("Stamps.com Request Data : %s" % (request_data))
                result = requests.post(url=url, data=request_data, headers=headers)
            except Exception as e:
                return {"success": False, "price": 0.0, "error_message": e, "warning_message": False}

            if result.status_code != 200:
                return {
                    "success": False,
                    "price": 0.0,
                    "error_message": "Rate Request Data Invalid! %s " % result.content,
                    "warning_message": False,
                }
            api = Response(result)
            result = api.dict()

            _logger.info("Stamps.com Rate Response Data : %s" % (result))
            existing_records = stamp_shipping_charge_obj.sudo().search([("sale_order_id", "=", order and order.id)])
            existing_records.sudo().unlink()

            res = (
                result.get("Envelope", {}).get("Body", {}).get("GetRatesResponse", {}).get("Rates", {}).get("Rate", {})
            )

            if res:
                if isinstance(res, dict):
                    res = [res]
                for rate in res:
                    _logger.info("In for Loop")
                    stamp_service_name = rate.get("ServiceType")
                    stamp_service_charge = rate.get("Amount")
                    stamp_service_shipping_day = rate.get("DeliverDays")
                    stamp_shipping_charge_obj.sudo().create(
                        {
                            "stamp_service_name": stamp_service_name,
                            "stamp_service_rate": stamp_service_charge,
                            "stamp_service_delivery_date": stamp_service_shipping_day,
                            "sale_order_id": order and order.id,
                        }
                    )
                stamp_service_charge_id = stamp_shipping_charge_obj.sudo().search(
                    [("sale_order_id", "=", order and order.id)], order="stamp_service_rate", limit=1
                )
                stamps_delivery = self.env["delivery.carrier"].search(
                    [
                        ("delivery_type", "=", "stamps"),
                        "|",
                        ("is_dropshipping_delivery", "=", True),
                        ("is_barneys_delivery", "=", True),
                    ],
                    limit=1,
                )
                rate_line = order.stamp_shipping_charge_ids.filtered(
                    lambda ship_charge: ship_charge.stamp_service_name == stamps_delivery.stam_service_info
                )
                order.stamp_shipping_charge_id = rate_line and rate_line.id
                return {
                    "success": True,
                    "price": rate_line and rate_line.stamp_service_rate or 0.0,
                    "error_message": False,
                    "warning_message": False,
                }
                # if rate.get('Rate').get('ServiceType') == self.stam_service_info and rate.get('Rate').get('PackageType') == self.stamps_package_type:
                #     Amount = rate.get('Rate').get('Amount')
                #     return {'success': True, 'price':float(Amount), 'error_message': False, 'warning_message': False}
                # else:
                #     return {'success': False, 'price':0.0, 'error_message': "Error in rate response : %s "%(res), 'warning_message': False}
            if not res:
                return {
                    "success": False,
                    "price": 0.0,
                    "error_message": "Error Response %s" % (result),
                    "warning_message": False,
                }

    def stamps_label_request_data(self, picking=False):
        sender_id = (
            picking.picking_type_id
            and picking.picking_type_id.warehouse_id
            and picking.picking_type_id.warehouse_id.partner_id
        )
        receiver_id = picking.partner_id

        pound_for_kg = 35.274
        uom_id = self.env["product.template"]._get_weight_uom_id_from_ir_config_parameter()
        if uom_id.name == "lbs":
            weight_lb = round(picking.weight, 3)
        else:
            weight_lb = round(picking.weight * pound_for_kg, 3)

        # pound_for_kg = 2.20462
        # ounce_for_kg = 35.274
        # WeightLb = round(picking.shipping_weight * pound_for_kg, 3)
        # WeightOz = round(picking.shipping_weight * ounce_for_kg, 3)

        # check sender Address
        if not sender_id.zip or not sender_id.city or not sender_id.country_id:
            raise ValidationError("Please Define Proper Sender Address!")

        # check Receiver Address
        if not receiver_id.zip or not receiver_id.city or not receiver_id.country_id:
            raise ValidationError("Please Define Proper Recipient Address!")

        master_node = etree.Element("Envelope")
        master_node.attrib["xmlns"] = "http://schemas.xmlsoap.org/soap/envelope/"
        submater_node = etree.SubElement(master_node, "Body")
        root_node = etree.SubElement(submater_node, "CreateIndicium")
        root_node.attrib["xmlns"] = "http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111"
        # etree.SubElement(root_node, "Authenticator").text = self.company_id and self.company_id.stamps_authenticator

        shipment_data = etree.SubElement(root_node, "Credentials")

        etree.SubElement(shipment_data, "IntegrationID").text = "%s" % (
            self.company_id and self.company_id.stamps_integrator_id
        )
        etree.SubElement(shipment_data, "Username").text = "%s" % (self.company_id and self.company_id.stamps_user_name)
        etree.SubElement(shipment_data, "Password").text = "%s" % (self.company_id and self.company_id.stamps_password)
        etree.SubElement(root_node, "IntegratorTxID").text = "%s" % (picking.origin)

        shipment_data = etree.SubElement(root_node, "Rate")

        shipper_adress = etree.SubElement(shipment_data, "From")

        etree.SubElement(shipper_adress, "FullName").text = "%s" % (self.company_name)
        etree.SubElement(shipper_adress, "Address1").text = "%s" % (self.po_box)
        etree.SubElement(shipper_adress, "City").text = "%s" % (self.city)
        etree.SubElement(shipper_adress, "State").text = "%s" % (self.state)
        etree.SubElement(shipper_adress, "ZIPCode").text = "%s" % (self.zip_code)
        etree.SubElement(shipper_adress, "Country").text = "%s" % (self.country)
        etree.SubElement(shipper_adress, "PhoneNumber").text = "%s" % (sender_id.phone)
        etree.SubElement(shipper_adress, "EmailAddress").text = "%s" % (sender_id.email)

        receiver_adress = etree.SubElement(shipment_data, "To")
        etree.SubElement(receiver_adress, "FullName").text = "%s" % (receiver_id.name)
        etree.SubElement(receiver_adress, "Address1").text = "%s" % (receiver_id.street)
        etree.SubElement(receiver_adress, "City").text = "%s" % (receiver_id.city)
        etree.SubElement(receiver_adress, "State").text = "%s" % (
            receiver_id.state_id and receiver_id.state_id.code or ""
        )
        etree.SubElement(receiver_adress, "ZIPCode").text = "%s" % (receiver_id.zip)
        etree.SubElement(receiver_adress, "Country").text = "%s" % (
            receiver_id.country_id and receiver_id.country_id.code or ""
        )
        etree.SubElement(receiver_adress, "PhoneNumber").text = "%s" % (receiver_id.phone)
        etree.SubElement(receiver_adress, "EmailAddress").text = "%s" % (receiver_id.email)

        etree.SubElement(shipment_data, "ServiceType").text = "%s" % (
            picking.sale_id.stamp_shipping_charge_id.stamp_service_name
            if picking.sale_id.stamp_shipping_charge_id
            else self.stam_service_info
        )

        etree.SubElement(shipment_data, "WeightOz").text = "%s" % (weight_lb)
        etree.SubElement(shipment_data, "PackageType").text = "%s" % (self.stamps_package_type)
        etree.SubElement(shipment_data, "Length").text = "%s" % (
            self.stamps_packaging_id and self.stamps_packaging_id.packaging_length or 0.0
        )
        etree.SubElement(shipment_data, "Width").text = "%s" % (
            self.stamps_packaging_id and self.stamps_packaging_id.width or 0.0
        )
        etree.SubElement(shipment_data, "Height").text = "%s" % (
            self.stamps_packaging_id and self.stamps_packaging_id.height or 0.0
        )
        # current_date = datetime.strftime(datetime.now(pytz.utc), "%Y-%m-%d")
        # etree.SubElement(shipment_data, "ShipDate").text = str(picking.scheduled_date.strftime("%Y-%m-%d"))
        etree.SubElement(shipment_data, "ShipDate").text = str(datetime.today().strftime("%Y-%m-%d"))

        etree.SubElement(root_node, "ImageType").text = "Pdf"
        etree.SubElement(root_node, "Reference1").text = "%s" % (picking.origin)
        return etree.tostring(master_node)

    @api.model
    def stamps_send_shipping(self, pickings):
        response = []
        for picking in pickings:
            try:
                request_data = picking.carrier_id.stamps_label_request_data(picking)

                url = "%s" % (picking.carrier_id.company_id.stamps_api_url)
                headers = {
                    "SOAPAction": "http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111/CreateIndicium",
                    "Content-Type": 'text/xml; charset="utf-8"',
                }
                try:
                    _logger.info("Stamps.com Request Data : %s" % (request_data))
                    result = requests.post(url=url, data=request_data, headers=headers)
                except Exception as e:
                    raise ValidationError(e)

                if result.status_code != 200:
                    raise ValidationError(_("Label Request Data Invalid! %s ") % (result.content))
                api = Response(result)
                result = api.dict()

                _logger.info("Stamps.com Shipment Response Data : %s" % (result))

                res = result.get("Envelope", {}).get("Body", {}).get("CreateIndiciumResponse", {})
                if not res:
                    raise ValidationError(_("Error Response %s") % (result))
                TrackingNumber = res.get("TrackingNumber")
                StampsTxID = res.get("StampsTxID")
                stamps_URL = res.get("URL")
                Amount = res.get("Rate").get("Amount")

                message = _("Label created!<br/> <b>Label Tracking Number : </b>%s<br/> <b> Parcel Number : %s") % (
                    TrackingNumber,
                    StampsTxID,
                )
                picking.message_post(body=message)

                picking.carrier_tracking_ref = TrackingNumber
                picking.stamps_label_url = stamps_URL
                picking.stamps_tx_id = StampsTxID
                picking.stamps_shipping_rate = float(Amount) or 0.0

                shipping_data = {"exact_price": float(Amount) or 0.0, "tracking_number": TrackingNumber}
                response += [shipping_data]
            except Exception as e:
                raise ValidationError(e)
        return response

    def stamps_normalize_text(self, text):
        text = text.replace("&", "&amp;")
        return text and normalize("NFKD", text).encode("ascii", "ignore").decode("ascii") or None

    # def gls_get_tracking_link(self, pickings):
    #     res = ""
    #     for picking in pickings:
    #         link = self.company_id and self.company_id.gls_tracking_url
    #         res = '%s%s' % (link, picking.carrier_tracking_ref)
    #         if not res:
    #             raise ValidationError("Tracking URL Is Not Set!")
    #     return res
    #

    def stamps_cancel_shipment(self, picking):
        master_node = etree.Element("Envelope")
        master_node.attrib["xmlns"] = "http://schemas.xmlsoap.org/soap/envelope/"
        submater_node = etree.SubElement(master_node, "Body")
        root_node = etree.SubElement(submater_node, "CancelIndicium")
        root_node.attrib["xmlns"] = "http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111"
        shipment_data = etree.SubElement(root_node, "Credentials")
        etree.SubElement(shipment_data, "IntegrationID").text = "%s" % (
            self.company_id and self.company_id.stamps_integrator_id
        )
        etree.SubElement(shipment_data, "Username").text = "%s" % (self.company_id and self.company_id.stamps_user_name)
        etree.SubElement(shipment_data, "Password").text = "%s" % (self.company_id and self.company_id.stamps_password)
        etree.SubElement(root_node, "TrackingNumber").text = "%s" % (picking.carrier_tracking_ref)
        try:
            request_data = etree.tostring(master_node)
            url = "%s" % (self.company_id.stamps_api_url)
            headers = {
                "SOAPAction": "http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111/CancelIndicium",
                "Content-Type": 'text/xml; charset="utf-8"',
            }
            try:
                _logger.info("Stamps.com Request Data : %s" % (request_data))
                result = requests.post(url=url, data=request_data, headers=headers)
            except Exception as e:
                raise ValidationError(e)

            if result.status_code != 200:
                raise ValidationError(_("Label Request Data Invalid! %s ") % (result.content))
            api = Response(result)
            result = api.dict()
            if result.get("Envelope").get("Body").get("Fault"):
                raise ValidationError(result.get("Envelope").get("Body").get("Fault"))
            else:
                _logger.info("Stamps.com cancel Shipment Response Data : %s" % (result))

        except Exception as e:
            raise ValidationError(e)

    def stamps_get_tracking_link(self, pickings):
        return "https://www.stamps.com/shipstatus/?confirmation=%s" % pickings.carrier_tracking_ref
