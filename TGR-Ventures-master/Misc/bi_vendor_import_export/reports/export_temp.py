from odoo import models


class BiClientExport(models.AbstractModel):
    _name = "report.bi_vendor_import_export.vendor_export_temp"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Vendor List")

        format3 = workbook.add_format(
            {
                "bottom": True,
                "top": True,
                "right": True,
                "left": True,
                "valign": "vcenter",
                "font_size": 11,
                "bg_color": "#C1CBC3;",
            }
        )
        format4 = workbook.add_format(
            {
                "bottom": True,
                "top": True,
                "right": True,
                "left": True,
                "valign": "vcenter",
                "font_size": 11,
            }
        )

        format3.set_align("center")

        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 25)
        worksheet.set_column("D:D", 20)
        worksheet.set_column("E:E", 20)
        worksheet.set_column("F:F", 20)
        worksheet.set_column("G:G", 20)
        worksheet.set_column("H:H", 20)
        worksheet.set_column("I:I", 20)
        worksheet.set_column("J:J", 20)
        worksheet.set_column("K:K", 20)
        worksheet.set_column("L:L", 20)
        worksheet.set_column("M:M", 20)
        worksheet.set_column("N:N", 20)
        worksheet.set_column("O:O", 20)
        worksheet.set_column("P:P", 20)
        worksheet.set_column("Q:Q", 20)
        worksheet.set_column("R:R", 20)
        worksheet.set_column("S:S", 20)
        worksheet.set_column("T:T", 20)
        worksheet.set_column("U:U", 20)
        worksheet.set_column("V:V", 20)
        worksheet.set_column("W:W", 20)
        worksheet.set_column("X:X", 20)
        worksheet.set_column("Y:Y", 20)
        worksheet.set_column("Z:Z", 20)
        worksheet.set_column("AA:AA", 20)
        worksheet.set_column("AB:AB", 20)
        worksheet.set_column("AC:AC", 20)
        worksheet.set_column("AD:AD", 20)
        worksheet.set_column("AE:AE", 20)

        worksheet.set_row(0, 30)
        worksheet.set_default_row(28)

        worksheet.write("A1", "Vendor ID", format3)
        worksheet.write("B1", "Name", format3)
        worksheet.write("C1", "Street", format3)
        worksheet.write("D1", "Street2", format3)
        worksheet.write("E1", "City", format3)
        worksheet.write("F1", "State", format3)
        worksheet.write("G1", "Country", format3)
        worksheet.write("H1", "Zip", format3)
        worksheet.write("I1", "Vat", format3)
        worksheet.write("J1", "Vendor Class", format3)
        worksheet.write("K1", "Phone", format3)
        worksheet.write("L1", "Mobile", format3)
        worksheet.write("M1", "Email", format3)
        worksheet.write("N1", "Website", format3)
        worksheet.write("O1", "Payment Terms", format3)
        worksheet.write("P1", "Lead Days", format3)
        worksheet.write("Q1", "Delivery Method", format3)
        worksheet.write("R1", "Taxes", format3)
        worksheet.write("S1", "Acumatica Status", format3)
        worksheet.write("T1", "Attention", format3)
        worksheet.write("U1", "Vendor External ID", format3)
        worksheet.write("V1", "Curr. Rate Type", format3)
        worksheet.write("W1", "Payment Method", format3)
        worksheet.write("X1", "Payment By", format3)
        worksheet.write("Y1", "Warehouse", format3)
        worksheet.write("Z1", "Delivery Estimate", format3)
        worksheet.write("AA1", "Discount - Comments", format3)
        worksheet.write("AB1", "Ordering Method", format3)
        worksheet.write("AC1", "Password", format3)
        worksheet.write("AD1", "Username", format3)
        worksheet.write("AE1", "Tax Zone", format3)

        row = 2
        vendor = self.env["res.partner"].search([("is_supplier", "=", True)])
        for each in vendor:
            worksheet.write("A%s" % row, each.name, format4)
            worksheet.write("B%s" % row, each.vendor_code if each.vendor_code else "", format4)
            worksheet.write("C%s" % row, each.street if each.street else "", format4)
            worksheet.write("D%s" % row, each.street2 if each.street2 else "", format4)
            worksheet.write("E%s" % row, each.city if each.city else "", format4)
            worksheet.write("F%s" % row, each.state_id.name if each.state_id else "", format4)
            worksheet.write("G%s" % row, each.country_id.name if each.country_id else "", format4)
            worksheet.write("H%s" % row, each.zip if each.zip else "", format4)
            worksheet.write("I%s" % row, each.vat if each.vat else "", format4)
            worksheet.write("J%s" % row, each.vendor_class_id.name if each.vendor_class_id else "", format4)
            worksheet.write("K%s" % row, each.phone if each.phone else "", format4)
            worksheet.write("L%s" % row, each.mobile if each.mobile else "", format4)
            worksheet.write("M%s" % row, each.email if each.email else "", format4)
            worksheet.write("N%s" % row, each.website if each.website else "", format4)
            worksheet.write(
                "O%s" % row,
                each.property_supplier_payment_term_id.name if each.property_supplier_payment_term_id else "",
                format4,
            )
            worksheet.write("P%s" % row, each.lead_days if each.lead_days else "", format4)
            worksheet.write(
                "Q%s" % row,
                each.property_delivery_carrier_id.name if each.property_delivery_carrier_id else "",
                format4,
            )
            worksheet.write(
                "R%s" % row,
                ",".join(each.mapped("taxes_ids").mapped("name")) if each.taxes_ids else "",
                format4,
            )
            worksheet.write("S%s" % row, each.vendor_status if each.vendor_status else "", format4)
            worksheet.write("T%s" % row, each.vendor_attention if each.vendor_attention else "", format4)
            worksheet.write("U%s" % row, each.vendor_external_id if each.vendor_external_id else "", format4)
            worksheet.write("V%s" % row, each.vendor_rate_type if each.vendor_rate_type else "", format4)
            worksheet.write("W%s" % row, each.vendor_payment_method if each.vendor_payment_method else "", format4)
            worksheet.write("X%s" % row, each.vendor_payment_by if each.vendor_payment_by else "", format4)
            worksheet.write("Y%s" % row, each.vendor_warehouse if each.vendor_warehouse else "", format4)
            worksheet.write(
                "Z%s" % row, each.vendor_delivery_estimate if each.vendor_delivery_estimate else "", format4
            )
            worksheet.write("AA%s" % row, each.vendor_discount_comment if each.vendor_discount_comment else "", format4)
            worksheet.write("AB%s" % row, each.vendor_ordering_method if each.vendor_ordering_method else "", format4)
            worksheet.write("AC%s" % row, each.vendor_password if each.vendor_password else "", format4)
            worksheet.write("AD%s" % row, each.vendor_username if each.vendor_username else "", format4)
            worksheet.write("AE%s" % row, each.tax_zone if each.tax_zone else "", format4)

            row += 1
