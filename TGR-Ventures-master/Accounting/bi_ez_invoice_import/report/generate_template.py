from odoo import models


class GeneratemplateProductImport(models.AbstractModel):
    _name = "report.bi_ez_invoice_import.template_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Import Template")
        worksheet.set_column("A:A", 30)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 20)
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

        format_wrap_text = workbook.add_format({"text_wrap": "true"})

        worksheet.write("A1", "DATE", format_wrap_text)
        worksheet.write("B1", "ORDER NUMBER", format_wrap_text)
        worksheet.write("C1", "DELIVERY COUNTRY", format_wrap_text)
        worksheet.write("D1", "Account", format_wrap_text)
        worksheet.write("E1", "TAXABLE AMOUNT EURO", format_wrap_text)
        worksheet.write("F1", "TOTAL AMOUNT EURO", format_wrap_text)
        worksheet.write("G1", "Customer Journal ID ", format_wrap_text)
        worksheet.write("H1", "TAX RATE", format_wrap_text)
        worksheet.write("I1", "CUSTOMER", format_wrap_text)
