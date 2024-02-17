from collections import defaultdict

from odoo import models


class AccountEdiFormat(models.Model):
    _inherit = "account.edi.format"

    def _l10n_es_edi_get_invoices_info(self, invoice):
        res = super(AccountEdiFormat, self)._l10n_es_edi_get_invoices_info(invoice)
        import_invoice = self.env["import.invoice"].search([("move_id", "=", invoice.id)], limit=1)
        if import_invoice:
            partner_info = self.with_context(error_1117=True)._l10n_es_edi_get_partner_info(import_invoice.vendor_id)
            res[0]["IDFactura"]["IDEmisorFactura"] = partner_info
            res[0]["IDFactura"]["NumSerieFacturaEmisor"] = import_invoice.ref
            res[0]["IDFactura"]["IDEmisorFactura"].update({"NIF": invoice.company_id.vat[2:]})
            res[0]["FacturaRecibida"]["Contraparte"] = {
                **partner_info,
                "NombreRazon": import_invoice.vendor_id.name[:120],
            }
            res[0]["FacturaRecibida"]["ClaveRegimenEspecialOTrascendencia"] = "01"
            res[0]["FacturaRecibida"]["TipoFactura"] = "F5"
            tax_details = defaultdict(dict)
            tax_details.setdefault("DetalleIVA", [])
            tax_details["DetalleIVA"].append(
                {
                    "BaseImponible": round(import_invoice.amount, 2),
                    "TipoImpositivo": round(import_invoice.tax_id.amount, 2),
                    "CuotaSoportada": round(import_invoice.tax_amount, 2),
                }
            )
            res[0]["FacturaRecibida"]["DesgloseFactura"]["DesgloseIVA"] = tax_details
            res[0]["FacturaRecibida"]["ImporteTotal"] = round(import_invoice.amount_total, 2)
            res[0]["FacturaRecibida"]["CuotaDeducible"] = round(import_invoice.tax_amount, 2)
        return res

    def _post_invoice_edi(self, invoices):
        res = super(AccountEdiFormat, self)._post_invoice_edi(invoices)
        for inv in invoices:
            import_invoice = self.env["import.invoice"].search([("move_id", "=", inv.id)], limit=1)
            if res.get(self.env["account.move"], {}).get("error"):
                import_invoice.write({"error_message": res.get(self.env["account.move"], {}).get("error")})
        return res
