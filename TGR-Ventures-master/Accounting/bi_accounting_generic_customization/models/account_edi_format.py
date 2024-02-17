from odoo import models, fields, _
from lxml import html
from odoo.exceptions import UserError


class AccountEdiFormat(models.Model):
    _inherit = "account.edi.format"

    def _l10n_es_edi_get_invoices_info(self, invoices):
        eu_country_codes = set(self.env.ref("base.europe").country_ids.mapped("code"))

        self.env.ref("l10n_es_edi_sii.partner_simplified")

        info_list = []
        for invoice in invoices:
            # if invoice.send_import_invoice:
            #     com_partner = invoice.import_invoice_vendor_id
            # else:
            com_partner = invoice.partner_id
            is_simplified = True if not bool(invoice.partner_id.vat) else False

            info = {
                "PeriodoLiquidacion": {
                    "Ejercicio": str(invoice.date.year),
                    "Periodo": str(invoice.date.month).zfill(2),
                },
                "IDFactura": {
                    "FechaExpedicionFacturaEmisor": invoice.invoice_date.strftime("%d-%m-%Y"),
                },
            }

            if invoice.is_sale_document():
                invoice_node = info["FacturaExpedida"] = {}
            else:
                invoice_node = info["FacturaRecibida"] = {}

            # === Partner ===

            partner_info = self._l10n_es_edi_get_partner_info(com_partner)

            # === Invoice ===

            if invoice.move_type in ["out_invoice", "out_refund"]:
                invoice_node["DescripcionOperacion"] = "SEEDS"
            elif invoice.move_type in ["in_invoice", "in_refund"]:
                doc = html.fromstring(invoice.narration)
                words = "".join(doc.xpath("//text()")).split()
                text = " ".join(words)
                invoice_node["DescripcionOperacion"] = text
            else:
                invoice_node["DescripcionOperacion"] = ""
            if invoice.is_sale_document():
                info["IDFactura"]["IDEmisorFactura"] = {"NIF": invoice.company_id.vat[2:]}
                if invoice.is_accumilative_invoice:
                    info["IDFactura"]["NumSerieFacturaEmisor"] = invoice.initial_series
                    info["IDFactura"]["NumSerieFacturaEmisorResumenFin"] = invoice.final_series
                # elif invoice.send_import_invoice:
                #     info['IDFactura']['NumSerieFacturaEmisor'] = invoice.import_invoice_ref
                else:
                    info["IDFactura"]["NumSerieFacturaEmisor"] = invoice.name[:60]
                if not is_simplified:
                    invoice_node["Contraparte"] = {
                        **partner_info,
                        "NombreRazon": com_partner.name[:120],
                    }
                if invoice.is_accumilative_invoice:
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "01"
                elif invoice.line_ids and "OSS" in invoice.line_ids.mapped("tax_tag_ids").mapped("name"):
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "17"
                elif (
                    bool(invoice.partner_id.vat)
                    and invoice.partner_id.vat[0:2] == "GB"
                    and com_partner.country_id.code not in eu_country_codes
                ):
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "02"
                elif bool(invoice.partner_id.vat) and invoice.partner_id.country_id.code == "CH":
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "02"
                elif bool(invoice.partner_id.vat) and invoice.partner_id.country_id.code == "US":
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "01"
                elif bool(invoice.partner_id.vat) and invoice.partner_id.country_id.code == "NO":
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "02"
                elif bool(invoice.partner_id.vat) and invoice.partner_id.country_id.code == "ZA":
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "02"
                elif not com_partner.country_id or com_partner.country_id.code in eu_country_codes:
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "01"
                elif (
                    bool(invoice.partner_id.vat)
                    and invoice.partner_id.vat[0:2] != "ES"
                    and com_partner.country_id.code not in eu_country_codes
                ):
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "01"
                elif bool(invoice.partner_id.vat) and com_partner.country_id.code not in eu_country_codes:
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "02"
                elif invoice.invoice_line_ids and any(
                    tax in [102]
                    for tax in invoice.invoice_line_ids[0].mapped("tax_ids").ids
                ):
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "02"
                else:
                    # invoice_node['ClaveRegimenEspecialOTrascendencia'] = '02'
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "01"
            else:
                info["IDFactura"]["IDEmisorFactura"] = partner_info
                # if invoice.send_import_invoice:
                #     info['IDFactura']['NumSerieFacturaEmisor'] = invoice.import_invoice_ref
                #     info['IDFactura']['IDEmisorFactura'].update({'NIF': invoice.company_id.vat[2:]})
                # else:
                info["IDFactura"]["NumSerieFacturaEmisor"] = invoice.ref[:60]
                if invoice.move_type in ["out_invoice", "out_refund"]:
                    if not is_simplified:
                        invoice_node["Contraparte"] = {
                            **partner_info,
                            "NombreRazon": com_partner.name[:120],
                        }
                else:
                    invoice_node["Contraparte"] = {
                        **partner_info,
                        "NombreRazon": com_partner.name[:120],
                    }
                    # if invoice.send_import_invoice:
                    #     invoice_node['IDEmisorFactura'] = {'NIF': invoice.company_id.vat[2:]}
                if invoice.l10n_es_registration_date:
                    invoice_node["FechaRegContable"] = invoice.l10n_es_registration_date.strftime("%d-%m-%Y")
                else:
                    invoice_node["FechaRegContable"] = fields.Date.context_today(self).strftime("%d-%m-%Y")

                com_partner.country_id.code
                if invoice.invoice_line_ids and any(
                    tax in [39, 40, 41, 48, 49, 50, 51, 116, 117]
                    for tax in invoice.invoice_line_ids[0].mapped("tax_ids").ids
                ):
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "09"  # For Intra-Com
                elif invoice.is_accumilative_invoice:
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "01"
                # elif invoice.send_import_invoice:
                #     invoice_node['ClaveRegimenEspecialOTrascendencia'] = '01'
                elif invoice.partner_id.country_id.code == "ES":
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "01"
                elif invoice.partner_id.country_id.code in eu_country_codes and bool(invoice.partner_id.vat):
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "01"
                elif invoice.partner_id.country_id.code not in eu_country_codes:
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "01"
            if invoice.is_accumilative_invoice:
                invoice_node["TipoFactura"] = "F4"
            # elif invoice.send_import_invoice:
            #     invoice_node['TipoFactura'] = 'F5'
            elif invoice.move_type == "out_invoice":
                invoice_node["TipoFactura"] = "F2" if is_simplified else "F1"
            elif invoice.move_type == "out_refund":
                invoice_node["TipoFactura"] = "R5" if is_simplified else "R4"
                invoice_node["TipoRectificativa"] = "I"
                # origin = invoice.original_invoice_id
                # invoice_node["ImporteRectificacion"] = {
                #     "BaseRectificada": abs(origin.amount_untaxed_signed),
                #     "CuotaRectificada": (
                #         origin.amount_total_signed - origin.amount_untaxed_signed
                #     ),
                # }
            elif invoice.move_type == "in_invoice":
                invoice_node["TipoFactura"] = "F1"
            elif invoice.move_type == "in_refund":
                invoice_node["TipoFactura"] = "R4"
                invoice_node["TipoRectificativa"] = "I"

            # === Taxes ===

            sign = -1 if invoice.is_sale_document() else 1

            if invoice.is_sale_document():
                # Customer invoices

                if (
                    invoice.partner_id.country_id.code != "ES"
                    and invoice.partner_id.country_id.code in eu_country_codes
                    and not bool(invoice.partner_id.vat)
                ):
                    tax_details_info_vals = self._l10n_es_edi_get_invoices_tax_details_info(invoice)
                    invoice_node["TipoDesglose"] = {"DesgloseFactura": tax_details_info_vals["tax_details_info"]}
                    invoice_node["ImporteTotal"] = round(
                        sign * (tax_details_info_vals["tax_details"]["base_amount"]), 2
                    )
                elif com_partner.country_id.code in ("ES", False) and not (com_partner.vat or "").startswith("ESN"):
                    tax_details_info_vals = self._l10n_es_edi_get_invoices_tax_details_info(invoice)
                    invoice_node["TipoDesglose"] = {"DesgloseFactura": tax_details_info_vals["tax_details_info"]}

                    invoice_node["ImporteTotal"] = round(
                        sign
                        * (
                            tax_details_info_vals["tax_details"]["base_amount"]
                            + tax_details_info_vals["tax_details"]["tax_amount"]
                            - tax_details_info_vals["tax_amount_retention"]
                        ),
                        2,
                    )
                else:
                    tax_details_info_service_vals = self._l10n_es_edi_get_invoices_tax_details_info(
                        invoice, filter_invl_to_apply=lambda x: any(t.tax_scope == "service" for t in x.tax_ids)
                    )
                    tax_details_info_consu_vals = self._l10n_es_edi_get_invoices_tax_details_info(
                        invoice, filter_invl_to_apply=lambda x: any(t.tax_scope == "consu" for t in x.tax_ids)
                    )
                    if tax_details_info_service_vals["tax_details_info"]:
                        invoice_node.setdefault("TipoDesglose", {})
                        invoice_node["TipoDesglose"].setdefault("DesgloseTipoOperacion", {})
                        invoice_node["TipoDesglose"]["DesgloseTipoOperacion"][
                            "PrestacionServicios"
                        ] = tax_details_info_service_vals["tax_details_info"]
                    if tax_details_info_consu_vals["tax_details_info"]:
                        invoice_node.setdefault("TipoDesglose", {})
                        invoice_node["TipoDesglose"].setdefault("DesgloseTipoOperacion", {})
                        invoice_node["TipoDesglose"]["DesgloseTipoOperacion"]["Entrega"] = tax_details_info_consu_vals[
                            "tax_details_info"
                        ]
                    if not invoice_node.get("TipoDesglose"):
                        raise UserError(
                            _(
                                "In case of a foreign customer, you need to configure the tax scope on taxes:\n%s",
                                "\n".join(invoice.line_ids.tax_ids.mapped("name")),
                            )
                        )

                    invoice_node["ImporteTotal"] = round(
                        sign
                        * (
                            tax_details_info_service_vals["tax_details"]["base_amount"]
                            + tax_details_info_service_vals["tax_details"]["tax_amount"]
                            - tax_details_info_service_vals["tax_amount_retention"]
                            + tax_details_info_consu_vals["tax_details"]["base_amount"]
                            + tax_details_info_consu_vals["tax_details"]["tax_amount"]
                            - tax_details_info_consu_vals["tax_amount_retention"]
                        ),
                        2,
                    )

            else:
                # Vendor bills

                tax_details_info_isp_vals = self._l10n_es_edi_get_invoices_tax_details_info(
                    invoice,
                    filter_invl_to_apply=lambda x: any(t for t in x.tax_ids if t.l10n_es_type == "sujeto_isp"),
                )
                tax_details_info_other_vals = self._l10n_es_edi_get_invoices_tax_details_info(
                    invoice,
                    filter_invl_to_apply=lambda x: not any(t for t in x.tax_ids if t.l10n_es_type == "sujeto_isp"),
                )

                invoice_node["DesgloseFactura"] = {}
                if tax_details_info_isp_vals["tax_details_info"]:
                    invoice_node["DesgloseFactura"]["InversionSujetoPasivo"] = tax_details_info_isp_vals[
                        "tax_details_info"
                    ]
                # if invoice.send_import_invoice:
                #     tax_details = defaultdict(dict)
                #     tax_details.setdefault('DetalleIVA', [])
                #     tax_details['DetalleIVA'].append({
                #         'BaseImponible': round(invoice.import_invoice_amount,2),
                #         'TipoImpositivo': round(invoice.import_invoice_tax_id.amount,2),
                #         'CuotaSoportada': round(invoice.import_invoice_tax_amount,2),
                #     })
                #     invoice_node['DesgloseFactura']['DesgloseIVA'] = tax_details
                if tax_details_info_other_vals["tax_details_info"]:
                    invoice_node["DesgloseFactura"]["DesgloseIVA"] = tax_details_info_other_vals["tax_details_info"]
                # if invoice.send_import_invoice:
                #     invoice_node['ImporteTotal'] = round(invoice.import_invoice_amount_total,2)
                if invoice.amount_tax > 0:
                    invoice_node["ImporteTotal"] = round(
                        sign
                        * (
                            tax_details_info_isp_vals["tax_details"]["base_amount"]
                            + tax_details_info_isp_vals["tax_details"]["tax_amount"]
                            - tax_details_info_isp_vals["tax_amount_retention"]
                            + tax_details_info_other_vals["tax_details"]["base_amount"]
                            + tax_details_info_other_vals["tax_details"]["tax_amount"]
                            - tax_details_info_other_vals["tax_amount_retention"]
                        ),
                        2,
                    )
                else:
                    invoice_node["ImporteTotal"] = round(
                        sign
                        * (
                            tax_details_info_isp_vals["tax_details"]["base_amount"]
                            # + tax_details_info_isp_vals['tax_details']['tax_amount']
                            - tax_details_info_isp_vals["tax_amount_retention"]
                            + tax_details_info_other_vals["tax_details"]["base_amount"]
                            # + tax_details_info_other_vals['tax_details']['tax_amount']
                            - tax_details_info_other_vals["tax_amount_retention"]
                        ),
                        2,
                    )

                # if invoice.send_import_invoice:
                #     invoice_node['CuotaDeducible'] = round(invoice.import_invoice_tax_amount,2)
                # else:
                invoice_node["CuotaDeducible"] = round(
                    sign
                    * (
                        tax_details_info_isp_vals["tax_amount_deductible"]
                        + tax_details_info_other_vals["tax_amount_deductible"]
                    ),
                    2,
                )

            info_list.append(info)
        return info_list