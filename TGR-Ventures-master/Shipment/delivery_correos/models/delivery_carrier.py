###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################

from odoo import fields, models
import base64
import xml.etree.ElementTree as ET
from datetime import datetime
from io import StringIO
from unicodedata import normalize

import base64
import requests
from odoo import _, exceptions, fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[("correos", "Correos")],
        ondelete={"correos": "set default"},
    )
    correos_username = fields.Char(
        string="User",
        help="Usernane for Correos webservice",
    )
    correos_password = fields.Char(
        string="Password",
        help="Password for Correos webservice",
    )
    correos_username_test = fields.Char(
        string="Username test",
        help="Username for test environment",
    )
    correos_password_test = fields.Char(
        string="Password test",
        help="Password for test environment",
    )
    correos_labeller_code = fields.Char(
        string="Labeller code",
    )
    service_type = fields.Char(
        string="Service Type",
    )
    is_international = fields.Boolean(
        string="Is International",
    )

    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    zip = fields.Char(string="Zip")
    city = fields.Char(string="City")
    state_id = fields.Many2one("res.country.state", string="Fed. State", domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one("res.country", string="Country")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    vat = fields.Char(
        string="Vat",
    )

    def correos_send(self, data):
        if self.prod_environment:
            url = "https://preregistroenvios.correos.es/preregistroenvios"
            credentials = self.correos_username + ":" + self.correos_password
        else:
            url = "https://preregistroenviospre.correos.es/preregistroenvios"
            credentials = self.correos_username_test + ":" + self.correos_password_test
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

    def correos_send_shipping(self, picking):
        return [self.correos_create_shipping(p) for p in picking]

    def correos_normalize_text(self, text):
        text = text.replace("&", "&amp;")
        return text and normalize("NFKD", text).encode("ascii", "ignore").decode("ascii") or None

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
        data = base64.b64decode(root.find(".//Fichero").text)
        picking.message_post(
            body="Correos %s" % picking.carrier_tracking_ref,
            attachments=[("COR-{}.{}".format(picking.carrier_tracking_ref, "pdf"), data)],
        )
        # picking.attachment_label = "COR-%s.%s" % ((picking.carrier_tracking_ref, "pdf"), data)
        name_attach = "COR-{}.{}".format(picking.carrier_tracking_ref, "pdf")
        attachment_id = self.env["ir.attachment"].search([("name", "=", name_attach)])
        if attachment_id:
            picking.attachment_label_id = attachment_id.id
            picking.attachment_label = attachment_id.datas
        return {
            "tracking_number": picking.carrier_tracking_ref,
            "exact_price": 0,
        }

    def _correos_prepare_create_shipping(self, picking):
        self.ensure_one()
        phone = (
            picking.partner_id.phone
            if picking.partner_id.phone
            else (picking.partner_id.mobile if picking.partner_id.mobile else "000")
        )
        shipping_weight = 0.045
        picking.partner_id.street2 if (picking.partner_id.street2) else ""
        picking_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        line_1 = "<soapenv:Envelope "
        line_2 = 'xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"'
        line_3 = 'xmlns="http://www.correos.es/iris6/services/'
        partner_address = " ".join([s for s in [picking.partner_id.street, picking.partner_id.street2] if s])
        if self.is_international:
            direction = f"{self.street},{self.street2 if self.street2 else ''}"
            localidad = self.city if self.city else self.state_id.name
            xml = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:prer="http://www.correos.es/iris6/services/preregistroetiquetas">
                <soapenv:Header/>
                <soapenv:Body>
                    <prer:PreregistroEnvio>
                        <prer:FechaOperacion>{}</prer:FechaOperacion>
                        <prer:CodEtiquetador>{}</prer:CodEtiquetador>
                        <prer:Care>000000</prer:Care>
                        <prer:TotalBultos>1</prer:TotalBultos>
                        <prer:ModDevEtiqueta>2</prer:ModDevEtiqueta>
                        <prer:Remitente>
                            <prer:Identificacion>
                                <prer:Nombre>{}</prer:Nombre>
                                <prer:Nif>{}</prer:Nif>
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
                            <prer:Pais>{}</prer:Pais>
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
                                <prer:TipoEnvio>1</prer:TipoEnvio>
                                <prer:EnvioComercial>S</prer:EnvioComercial>
                                <prer:FacturaSuperiora500>N</prer:FacturaSuperiora500>
                                <prer:DescAduanera>
                                    <prer:DATOSADUANA>
                                        <prer:Cantidad>1</prer:Cantidad>
                                        <prer:Descripcion>322</prer:Descripcion>
                                        <prer:Pesoneto>1</prer:Pesoneto>
                                        <prer:Valorneto>1</prer:Valorneto>
                                    </prer:DATOSADUANA>
                                </prer:DescAduanera>
                            </prer:Aduana>
                        </prer:Envio>
                    </prer:PreregistroEnvio>
                </soapenv:Body>
                </soapenv:Envelope>""".format(
                picking_date,
                self.correos_labeller_code,
                picking.company_id.name,
                self.vat,
                "",
                direction,
                localidad,
                self.zip,
                self.phone,
                self.email,
                picking.partner_id.name,
                partner_address,
                picking.partner_id.city,
                picking.partner_id.zip,
                picking.partner_id.country_id.code,
                phone,
                self.service_type,
                picking.origin,
                shipping_weight,
            )
            return self.correos_normalize_text(xml)
        else:
            xml = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:prer="http://www.correos.es/iris6/services/preregistroetiquetas">
            <soapenv:Header/>
            <soapenv:Body>
                <prer:PreregistroEnvio>
                    <prer:FechaOperacion>{}</prer:FechaOperacion>
                    <prer:CodEtiquetador>{}</prer:CodEtiquetador>
                    <prer:Care>000000</prer:Care>
                    <prer:TotalBultos>1</prer:TotalBultos>
                    <prer:ModDevEtiqueta>2</prer:ModDevEtiqueta>
                    <prer:Remitente>
                        <prer:Identificacion>
                            <prer:Nombre>{}</prer:Nombre>
                            <prer:Nif>{}</prer:Nif>
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
                        <prer:CP>{}</prer:CP>
                        <prer:Pais>{}</prer:Pais>
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
                            <prer:TipoEnvio>1</prer:TipoEnvio>
                            <prer:EnvioComercial>S</prer:EnvioComercial>
                            <prer:FacturaSuperiora500>N</prer:FacturaSuperiora500>
                        </prer:Aduana>
                    </prer:Envio>
                </prer:PreregistroEnvio>
            </soapenv:Body>
            </soapenv:Envelope>""".format(
                picking_date,
                self.correos_labeller_code,
                picking.company_id.name,
                picking.company_id.vat,
                picking.company_id.street,
                picking.company_id.street2,
                picking.company_id.city,
                picking.company_id.zip,
                picking.company_id.phone,
                picking.company_id.email,
                picking.partner_id.name,
                partner_address,
                picking.partner_id.city,
                picking.partner_id.zip,
                picking.partner_id.country_id.code,
                phone,
                self.service_type,
                picking.origin,
                shipping_weight,
            )
        return self.correos_normalize_text(xml)
