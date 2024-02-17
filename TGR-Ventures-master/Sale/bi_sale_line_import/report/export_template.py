from odoo import models


class ExportTemplateLineImport(models.AbstractModel):
    _name = "report.bi_sale_line_import.line_export_template_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Export Template Import"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Sale Line Import Template")
        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 20)
        worksheet.set_column("D:D", 20)
        worksheet.set_column("E:E", 20)
        worksheet.set_column("F:F", 20)
        worksheet.set_column("G:G", 20)

        format_wrap_text = workbook.add_format({"text_wrap": "true", "bold": "true"})

        worksheet.write("A1", "SKU Code", format_wrap_text)
        worksheet.write("B1", "Quantity", format_wrap_text)
        worksheet.write("C1", "Unit Price", format_wrap_text)
        worksheet.write("D1", "Tax", format_wrap_text)
        worksheet.write("E1", "Discount Percent", format_wrap_text)
