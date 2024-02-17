from odoo import fields, models, _
import requests
import base64
import requests
from odoo.exceptions import ValidationError
from unicodedata import normalize
from odoo.addons.stamps_shipping_integration.models.stamps_response import Response


class StockPicking(models.Model):
    _inherit = "stock.picking"
    stamps_label_url = fields.Char(string="Stamps.com Label URL", copy=False)
    stamps_tx_id = fields.Char(string="Stamps.com Tx ID", copy=False)
    stamps_shipping_rate = fields.Float("Stamps Shipping Rate")

    def reprint_stamps_label(self):
        for picking in self:
            if picking.carrier_id.delivery_type != "stamps":
                raise ValidationError(_("This is not STAMPS shipment."))
            if not picking.carrier_tracking_ref:
                raise ValidationError(_("Tracking reference not available."))
            reprint_request_xml = f"""
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body>
    <ReprintIndicium xmlns="http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111">
    <indiciumRequest>
        <Credentials>
            <IntegrationID>{self.company_id.stamps_integrator_id}</IntegrationID>
            <Username>{self.company_id.stamps_user_name}</Username>
            <Password>{self.company_id.stamps_password}</Password>
        </Credentials>
        <TrackingNumber>{picking.carrier_tracking_ref}</TrackingNumber>
        <ImageType>Pdf</ImageType>
        <ImageDpi>ImageDpi300</ImageDpi>
        <EltronPrinterDpiType>Default</EltronPrinterDpiType>
        <RotationDegrees>0</RotationDegrees>
        <HorizontalOffset>0</HorizontalOffset>
        <VerticalOffset>0</VerticalOffset>
        <PrintDensity>0</PrintDensity>
        <PaperSize>Default</PaperSize>
        <StartRow>0</StartRow>
        <StartColumn>0</StartColumn>
        <ReturnImageData>true</ReturnImageData>
    </indiciumRequest>
    </ReprintIndicium>
</soap:Body>
</soap:Envelope>
            """
            reprint_request_xml = self.stamps_normalize_text(reprint_request_xml)
            reprint_request_url = "%s" % (picking.company_id.stamps_api_url)
            reprint_request_headers = {
                "SOAPAction": "http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111/ReprintIndicium",
                "Content-Type": 'text/xml; charset="utf-8"',
                "Content-Lenght": str(len(reprint_request_xml)),
            }
            try:
                response = requests.post(
                    url=reprint_request_url, data=reprint_request_xml, headers=reprint_request_headers
                )
                xml_dict = Response(response).dict()
                image_data = (
                    xml_dict.get("Envelope", False)
                    and xml_dict["Envelope"].get("Body", False)
                    and xml_dict["Envelope"]["Body"].get("ReprintIndiciumResponse", False)
                    and xml_dict["Envelope"]["Body"]["ReprintIndiciumResponse"].get("ReprintIndiciumResult", False)
                    and xml_dict["Envelope"]["Body"]["ReprintIndiciumResponse"]["ReprintIndiciumResult"].get(
                        "ImageData", False
                    )
                    and xml_dict["Envelope"]["Body"]["ReprintIndiciumResponse"]["ReprintIndiciumResult"][
                        "ImageData"
                    ].get("base64Binary", False)
                )
                if not image_data:
                    raise ValidationError(_("Label not received."))
                data = base64.b64decode(image_data)
                picking.message_post(
                    body="Stamps Label %s" % picking.carrier_tracking_ref,
                    attachments=[("STAMPS-{}.{}".format(picking.carrier_tracking_ref, "pdf"), data)],
                )
                name_attach = "STAMPS-{}.{}".format(picking.carrier_tracking_ref, "pdf")
                attachment_id = self.env["ir.attachment"].search([("name", "=", name_attach)])
                if attachment_id:
                    picking.attachment_label_id = attachment_id.id
                    picking.attachment_label = attachment_id.datas
            except Exception as e:
                raise ValidationError(e)

    def stamps_normalize_text(self, text):
        text = text.replace("&", "&amp;")
        return text and normalize("NFKD", text).encode("ascii", "ignore").decode("ascii") or None

    def get_stamps_rate_shipment(self):
        for picking in self:
            order = self.env["sale.order"].search([("picking_ids", "=", picking.ids)])
            picking.carrier_id.stamps_rate_shipment(order)

    # def _compute_stamps_shipping_rate(self):
    #     for picking in self:
    #         if picking.carrier_id.delivery_type != "stamps":
    #             picking.stamps_shipping_rate = 0
    #         else:
    #             order = self.env['sale.order'].search([
    #                 ('picking_ids', '=', picking.ids)
    #             ])
    #             rate_line = order.stamp_shipping_charge_ids.filtered(
    #                 lambda ship_charge: ship_charge.stamp_service_name == picking.carrier_id.stam_service_info
    #             )
    #             if rate_line:
    #                 picking.stamps_shipping_rate = rate_line.stamp_service_rate
    #             else:
    #                 picking.stamps_shipping_rate = 0

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for picking in self.filtered(lambda pick: pick.carrier_id and pick.carrier_id.delivery_type == "stamps"):
            picking.get_stamps_rate_shipment()
        return res

    def generate_shipment(self):
        for rec in self:
            if not rec.carrier_tracking_ref and rec.carrier_id.delivery_type == "stamps" and rec.state == "done":
                return self.env["delivery.carrier"].stamps_send_shipping(rec)
