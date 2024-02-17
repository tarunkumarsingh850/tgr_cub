from odoo import models


class ExportemplateInvoice(models.AbstractModel):
    _name = "report.bi_import_invoice_line.export_template_invoice_line"
    _inherit = "report.report_xlsx.abstract"
    _description = "Export Template Invoice Line"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Import Template")
        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 20)
        worksheet.set_column("D:D", 20)
        worksheet.set_column("E:E", 20)
        format_wrap_text = workbook.add_format({"text_wrap": "true"})
        worksheet.write("A1", "Product SKU", format_wrap_text)
        worksheet.write("B1", "Quantity", format_wrap_text)
        worksheet.write("C1", "Price", format_wrap_text)
        worksheet.write("D1", "Tax", format_wrap_text)
        worksheet.write("E1", "Discount %", format_wrap_text)
