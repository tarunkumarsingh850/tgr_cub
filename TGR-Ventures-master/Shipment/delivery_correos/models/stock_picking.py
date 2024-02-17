###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
import base64
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from io import StringIO
from unicodedata import normalize
import binascii

import base64

# from django.http import HttpResponse

import requests
from odoo import _, exceptions, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    correos_last_request = fields.Text(
        string="Last Correos request",
        help="Used for issues debugging",
        copy=False,
        readonly=True,
    )
    correos_last_response = fields.Text(
        string="Last Correos response",
        help="Used for issues debugging",
        copy=False,
        readonly=True,
    )

    attachment_label = fields.Binary(
        string="Attachment Label",
    )

    attachment_label_id = fields.Many2one(
        string="Attachment",
        comodel_name="ir.attachment",
    )

    def correos_send(self, data):
        if self.carrier_id.prod_environment:
            url = "https://preregistroenvios.correos.es/preregistroenvios"
            credentials = self.carrier_id.correos_username + ":" + self.carrier_id.correos_password
        else:
            url = "https://preregistroenviospre.correos.es/preregistroenvios"
            credentials = self.carrier_id.correos_username_test + ":" + self.carrier_id.correos_password_test
        credentials = credentials.encode()
        credentials_encode = base64.b64encode(credentials)
        headers = {
            "Content-type": "text/xml;charset=utf-8",
            "Content-Lenght": str(len(data)),
            "Authorization": "Basic {}".format(credentials_encode.decode()),
            "SOAPAction": "PreRegistro",
        }
        res = requests.post(url, headers=headers, data=data)
        return res

    def correos_send_shipping(self):
        return [self.correos_create_shipping(p) for p in self]

    def correos_normalize_text(self, text):
        text = text.replace("&", "&amp;")
        return text and normalize("NFKD", text).encode("ascii", "ignore").decode("ascii") or None

    def correos_reprint_label(self):
        for picking in self:
            picking.carrier_id.correos_send_shipping(picking)

    def _correos_prepare_create_shipping(self, picking):
        self.ensure_one()
        phone = (
            picking.partner_id.phone
            if picking.partner_id.phone
            else (picking.partner_id.mobile if picking.partner_id.mobile else "000")
        )
        shipping_weight = 0.045
        street2 = picking.partner_id.street2 if (picking.partner_id.street2) else ""
        picking_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        line_1 = "<soapenv:Envelope "
        line_2 = 'xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"'
        line_3 = 'xmlns="http://www.correos.es/iris6/services/'
        partner_address = " ".join([s for s in [picking.partner_id.street, picking.partner_id.street2] if s])
        xml = """
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:prer="http://www.correos.es/iris6/services/preregistroetiquetas">
            <soapenv:Header/>
            <soapenv:Body>
                <prer:PreregistroEnvio>
                    <prer:FechaOperacion>{}</prer:FechaOperacion>
                    <prer:CodEtiquetador>{}</prer:CodEtiquetador>
                    <prer:Care>000000</prer:Care>
                    <prer:TotalBultos>1</prer:TotalBultos>
                    <prer:ModDevEtiqueta>1</prer:ModDevEtiqueta>
                    <prer:Remitente>
                        <prer:Identificacion>
                            <prer:Nombre>{}</prer:Nombre>
                            <prer:Nif>12345678Z</prer:Nif>
                        </prer:Identificacion>
                        <prer:DatosDireccion>
                            <prer:TipoDireccion>{}</prer:TipoDireccion>
                            <prer:Direccion>{}</prer:Direccion>
                            <prer:Localidad>{}</prer:Localidad>
                        </prer:DatosDireccion>
                        <prer:CP>{}</prer:CP>
                        <prer:Telefonocontacto>{}</prer:Telefonocontacto>
                        <prer:Email>{}</prer:Email>
                    </prer:Remitente>
                    <prer:Destinatario>
                        <prer:Identificacion>
                            <prer:Nombre>{}</prer:Nombre>
                        </prer:Identificacion>
                        <prer:DatosDireccion>
                            <prer:Direccion>{}</prer:Direccion>
                            <prer:Localidad>{}</prer:Localidad>
                        </prer:DatosDireccion>
                        <prer:ZIP>{}</prer:ZIP>
                        <prer:Pais>CO</prer:Pais>
                        <prer:Telefonocontacto>{}</prer:Telefonocontacto>
                    </prer:Destinatario>
                    <prer:Envio>
                        <prer:CodProducto>{}</prer:CodProducto>
                        <prer:ReferenciaCliente>{}</prer:ReferenciaCliente>
                        <prer:TipoFranqueo>FP</prer:TipoFranqueo>
                        <prer:Pesos>
                            <prer:Peso>
                                <prer:TipoPeso>R</prer:TipoPeso>
                                <prer:Valor>{}</prer:Valor>
                            </prer:Peso>
                        </prer:Pesos>
                        <prer:InstruccionesDevolucion>D</prer:InstruccionesDevolucion>
                        <prer:Aduana>
                            <prer:TipoEnvio>2</prer:TipoEnvio>
                            <prer:EnvioComercial>S</prer:EnvioComercial>
                            <prer:FacturaSuperiora500>N</prer:FacturaSuperiora500>
                            <prer:DescAduanera>
                                <prer:DATOSADUANA>
                                    <prer:Cantidad>1</prer:Cantidad>
                                    <prer:Descripcion>322</prer:Descripcion>
                                    <prer:Pesoneto>3000</prer:Pesoneto>
                                    <prer:Valorneto>019856</prer:Valorneto>
                                </prer:DATOSADUANA>
                            </prer:DescAduanera>
                        </prer:Aduana>
                    </prer:Envio>
                </prer:PreregistroEnvio>
            </soapenv:Body>
            </soapenv:Envelope>""".format(
            picking_date,
            self.carrier_id.correos_labeller_code,
            picking.company_id.name,
            picking.company_id.street,
            street2,
            picking.company_id.city,
            # TODO DBT REGARDING THE XIP AND CITY
            picking.company_id.zip,
            picking.company_id.phone,
            picking.company_id.email,
            picking.partner_id.name,
            partner_address,
            picking.partner_id.city,
            picking.partner_id.zip,
            phone,
            self.carrier_id.service_type,
            picking.origin,
            int(shipping_weight),
        )
        return self.correos_normalize_text(xml)
        # </soapenv:Envelope>"""
        # return xml

    def _zebra_label_custom(self, label):
        return label

    def correos_create_shipping(self, picking):
        self.ensure_one()
        package_info = self._correos_prepare_create_shipping(picking)
        picking.write(
            {
                "correos_last_request": fields.Datetime.now(),
            }
        )
        response = self.correos_send(package_info)
        it = ET.iterparse(StringIO(response.text))
        for _index, el in it:
            prefix, has_namespace, postfix = el.tag.partition("}")
            if has_namespace:
                el.tag = postfix
        root = it.root
        errors = root.findall(".//faultstring") or root.findall(".//DescError") or []
        if errors:
            raise exceptions.UserError(_("Correos error: %s") % (", ".join(error.text for error in errors)))
        picking.write(
            {
                "correos_last_response": fields.Datetime.now(),
                "carrier_tracking_ref": root.find(".//CodEnvio").text,
            }
        )
        data = binascii.a2b_base64(str(root.find(".//Fichero").text))

        # data = base64.b64decode(str(root.find(".//Fichero").text), validate=True)

        # data = self.b64_to_pdf(str(root.find(".//Fichero").text))

        picking.message_post(
            body="Correos %s" % picking.carrier_tracking_ref,
            attachments=[("COR-{}.{}".format(picking.carrier_tracking_ref, "pdf"), data.content)],
        )
        # self.env['ir.attachment'].create({
        #     'name': 'Correos %s' % picking.carrier_tracking_ref,
        #     'datas': root.find('.//Fichero').text,
        #     # 'datas_fname': 'correos_%s' % picking.carrier_tracking_ref,
        #     'res_model': 'stock.picking',
        #     'res_id': picking.id,
        #     'mimetype': 'application/pdf',
        # })
        return {
            "tracking_number": picking.carrier_tracking_ref,
            "exact_price": 0,
        }

    def update_state(self, data):
        if data[0]["error"]["codError"] != "0":
            return _("Error code: %s, Error: %s") % (data[0]["error"]["codError"], data[0]["error"]["desError"])
        return "{}-{}-{}-{}".format(
            data[0]["eventos"][0]["fecEvento"],
            data[0]["eventos"][0]["horEvento"],
            data[0]["eventos"][0]["desTextoResumen"],
            data[0]["eventos"][0]["desTextoAmpliado"],
        )

    def correos_tracking_state_update(self, picking):
        self.ensure_one()
        if not self.correos_username or not self.correos_password:
            picking.tracking_state_history = _("Status cannot be checked, enter webservice carrier " "credentiasl")
            return
        credentials = self.correos_username + ":" + self.correos_password
        credentials = credentials.encode()
        credentials_encode = base64.b64encode(credentials)
        headers = {
            "Authorization": "Basic {}".format(credentials_encode.decode()),
            "Accept": "application/json",
        }
        url = (
            "https://localizador.correos.es/canonico/"
            "eventos_envio_servicio_auth/%s?codIdioma=ES&indUltEvento=S" % (picking.carrier_tracking_ref)
        )
        res = requests.get(url, headers=headers)
        response = json.loads(res.content)
        tracking_state = self.update_state(response)
        picking.tracking_state_history = tracking_state

    def correos_cancel_shipment(self, picking):
        raise NotImplementedError(
            _(
                """
            Correos API doesn't provide methods to cancel shipment"""
            )
        )

    def correos_get_tracking_link(self, picking):
        return "http://www.correos.es/comun/localizador/track.asp?numero=%s" % (picking.carrier_tracking_ref)

    def correos_rate_shipment(self, order):
        raise NotImplementedError(
            _(
                """
            Correos API doesn't provide methods to compute delivery
            rates, so you should relay on another price method instead or
            override this one in your custom code.
        """
            )
        )
