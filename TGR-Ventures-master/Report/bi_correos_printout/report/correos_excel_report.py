from odoo import models


class CorreosExcelReportXLsx(models.AbstractModel):
    _name = "report.bi_correos_printout.correos_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, records):
        format1 = workbook.add_format(
            {
                "font_size": 10,
                "align": "center",
                "valign": "vcenter",
                "font_name": "Calibri",
            }
        )
        header_format = workbook.add_format(
            {
                "font_size": 10,
                "align": "center",
                "valign": "vcenter",
                "font_name": "Calibri",
                "bold": True,
            }
        )
        table_main_header = workbook.add_format(
            {
                "bold": True,
                "font_size": 11,
                "align": "left",
                "valign": "vcenter",
                "border": 1,
            }
        )
        table_main_value = workbook.add_format(
            {
                "font_size": 11,
                "align": "left",
                "valign": "vcenter",
                "border": 1,
            }
        )

        worksheet = workbook.add_worksheet("Correos Report")
        # worksheet.set_row(11, )
        # worksheet.set_row(10, 10)
        worksheet.set_column("A:A", 25)
        worksheet.set_column("B:B", 25)
        worksheet.set_column("C:C", 25)
        worksheet.set_column("D:D", 25)
        worksheet.set_column("E:E", 25)
        worksheet.set_column("F:F", 25)
        worksheet.set_column("G:G", 25)
        worksheet.set_column("H:H", 25)
        worksheet.set_column("I:I", 25)
        worksheet.set_column("J:J", 25)
        worksheet.set_column("K:K", 25)
        worksheet.set_column("L:L", 25)
        worksheet.set_column("M:M", 25)
        worksheet.set_column("N:N", 25)
        worksheet.set_column("O:O", 25)
        worksheet.set_column("P:P", 25)
        worksheet.set_column("R:R", 25)
        worksheet.set_column("S:S", 25)
        worksheet.set_column("T:T", 25)
        worksheet.set_column("V:V", 25)
        worksheet.set_column("W:W", 25)
        worksheet.set_default_row(20)

        worksheet.merge_range(
            "A1:D1", "MANIFIESTO DETALLADO - OFICINA VIRTUAL: Carta certificada Internacional", table_main_header
        )

        get_records = self.env["report.bi_correos_printout.correos_pdf_report"]._get_report_values(records, data)

        worksheet.write("A3", "CLIENTE", table_main_header)
        worksheet.write("B3", records.carrier_id.name, table_main_value)
        worksheet.write("A4", "EXPEDIENTE", table_main_header)
        worksheet.write("B4", "", table_main_value)
        worksheet.write("A5", "CÓDIGO ETIQUETADOR", table_main_header)
        worksheet.write("B5", "", table_main_value)
        worksheet.write("A6", "FECHA DE GENERACIÓN", table_main_header)
        worksheet.write("B6", get_records["start_date"], table_main_value)
        worksheet.write("A7", "FECHA DE IMPRESIÓN", table_main_header)
        worksheet.write("B7", get_records["end_date"], table_main_value)

        worksheet.write("A8", "FORMA DE PAGO", table_main_header)
        worksheet.write("B8", "Pagado por contrato", table_main_value)

        worksheet.write("C3", "CÓDIGO DE MANIFIESTO", table_main_header)
        worksheet.write("D3", get_records["barcode"], table_main_value)

        worksheet.write("A10", "No ENVIO", table_main_header)
        worksheet.write("B10", "DEST./CONSIG.", table_main_header)
        worksheet.write("C10", "BULTOS", table_main_header)
        worksheet.write("D10", "KILOS", table_main_header)
        worksheet.write("E10", "PVP *", table_main_header)
        worksheet.write("F10", "REEMB", table_main_header)
        worksheet.write("G10", "VALOR DECLARAD", table_main_header)
        worksheet.write("H10", "VALORES AÑADIDOS", table_main_header)

        row = 11
        total_weight = 0.00
        total_qty = 0.00
        for picking in get_records["vals"]:
            total_qty = total_qty + 1
            total_weight = total_weight + 0.045
            worksheet.set_row(row - 1, 70)
            tracking_ref = "tracking_ref" in picking and picking["tracking_ref"] or ""
            partner = picking["partner"] and picking["partner"] + ",\n" or ""
            ref = "origin" in picking and picking["origin"] or ""
            street = picking["street"] and picking["street"] + ",\n" or ""
            city = picking["city"] and picking["city"] + ",\n" or ""
            state = picking["state"] and picking["state"] + ",\n" or ""
            country = picking["country"] and picking["country"] or ""

            worksheet.write(
                "A%s" % row, tracking_ref + "\n" + "Ref:" + ref + "\n" + "Observaciones:" + ref, table_main_value
            )
            worksheet.write("B%s" % row, partner + street + city + state + country, table_main_value)
            worksheet.write("C%s" % row, 1, table_main_value)
            worksheet.write("D%s" % row, 0.045, table_main_value)
            worksheet.write("E%s" % row, "", table_main_value)
            worksheet.write("F%s" % row, "", table_main_value)
            worksheet.write("G%s" % row, "", table_main_value)
            worksheet.write("H%s" % row, "", table_main_value)
            row += 1
        worksheet.write("B%s" % row, "TOTALES", table_main_value)
        worksheet.write("C%s" % row, total_qty, table_main_value)
        worksheet.write("D%s" % row, total_weight, table_main_value)
