from odoo import models


class ExportLPOTemplateProductImport(models.AbstractModel):
    _name = "report.bi_purchase_order_import.export_lpo_template_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Export Template Line Import"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Import Template")
        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 20)
        worksheet.set_column("D:D", 20)
        worksheet.set_column("E:E", 20)
        format_wrap_text = workbook.add_format({"text_wrap": "true"})
        worksheet.write("A1", "VENDOR", format_wrap_text)
        worksheet.write("B1", "SKU CODE", format_wrap_text)
        worksheet.write("C1", "WAREHOUSE", format_wrap_text)
        worksheet.write("D1", "QUANTITY", format_wrap_text)
        worksheet.write("E1", "UNIT PRICE", format_wrap_text)
