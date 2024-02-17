import requests
from odoo import _, fields, models
import logging
import xml.etree.ElementTree as etree
from odoo.exceptions import ValidationError
from odoo.addons.stamps_shipping_integration.models.stamps_response import Response

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"
    stamps_user_name = fields.Char(string="Stamps User Name", help="Provided By Stamps.com", copy=False)
    stamps_password = fields.Char(copy=False, string="Stamps Password", help="Provided By Stamps.com")
    stamps_integrator_id = fields.Char(string="Integrator ID", help="Provided By Stamps.com", copy=False)

    stamps_api_url = fields.Char(
        copy=False,
        string="Stamps API URL",
        help="API URL, Redirect to this URL when calling the API.",
        default="https://swsim.testing.stamps.com/swsim/swsimv111.asmx",
    )
    use_stamps_shipping_provider = fields.Boolean(
        copy=False,
        string="Are You Using Stamps.com?",
        help="If use stamps.com shipping Integration than value set TRUE.",
        default=False,
    )
    stamps_authenticator = fields.Text(string="Stamps.com Authenticator", help="Provided By Stamps.com", copy=False)

    def weight_convertion(self, weight_unit, weight):
        pound_for_kg = 2.20462
        ounce_for_kg = 35.274
        if weight_unit in ["LB", "LBS"]:
            return round(weight * pound_for_kg, 3)
        elif weight_unit in ["OZ", "OZS"]:
            return round(weight * ounce_for_kg, 3)
        else:
            return round(weight, 3)

    def generate_stamps_authenticator(self):
        url = "%s" % (self.stamps_api_url)
        headers = {
            "SOAPAction": "http://stamps.com/xml/namespace/2019/09/swsim/SwsimV84/AuthenticateUser",
            "Content-Type": 'text/xml; charset="utf-8"',
        }
        master_node = etree.Element("Envelope")
        master_node.attrib["xmlns"] = "http://schemas.xmlsoap.org/soap/envelope/"
        submater_node = etree.SubElement(master_node, "Body")

        root_node = etree.SubElement(submater_node, "AuthenticateUser")
        root_node.attrib["xmlns"] = "http://stamps.com/xml/namespace/2019/09/swsim/SwsimV84"
        shipment_data = etree.SubElement(root_node, "Credentials")

        etree.SubElement(shipment_data, "IntegrationID").text = "%s" % (self.stamps_integrator_id)
        etree.SubElement(shipment_data, "Username").text = "%s" % (self.stamps_user_name)
        etree.SubElement(shipment_data, "Password").text = "%s" % (self.stamps_password)
        request_data = etree.tostring(master_node)
        try:
            _logger.info("Stamps Authenticator Request Data : %s" % (request_data))
            result = requests.post(url=url, data=request_data, headers=headers)
        except Exception as e:
            raise ValidationError(e)
        if result.status_code != 200:
            raise ValidationError(_("Label Request Data Invalid! %s ") % (result.content))
        api = Response(result)
        result = api.dict()
        if (
            result.get("Envelope")
            and result.get("Envelope").get("Body")
            and result.get("Envelope").get("Body").get("AuthenticateUserResponse")
            and result.get("Envelope").get("Body").get("AuthenticateUserResponse").get("Authenticator")
        ):
            self.stamps_authenticator = (
                result.get("Envelope").get("Body").get("AuthenticateUserResponse").get("Authenticator")
            )
            return {
                "effect": {
                    "fadeout": "slow",
                    "message": "Yeah! Shipping Charge has been retrieved.",
                    "img_url": "/web/static/src/img/smile.svg",
                    "type": "rainbow_man",
                }
            }
        else:
            raise ValidationError("%s" % (result))
