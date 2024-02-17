from odoo import models


class ExportemplateProductImport(models.AbstractModel):
    _name = "report.bi_kit_specification_import.export_template_kit"
    _inherit = "report.report_xlsx.abstract"
    _description = "Export Template Line Import"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Import Template")
        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:B", 20)
        format_wrap_text = workbook.add_format({"text_wrap": "true"})
        worksheet.write("A1", "Product SKU", format_wrap_text)
        worksheet.write("B1", "Line SKU", format_wrap_text)
