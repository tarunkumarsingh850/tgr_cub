from odoo import models


class ExportAdjustImport(models.AbstractModel):
    _name = "report.bi_inv_adjustment_import.export_adj_template_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Export"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Import Template")
        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 20)
        worksheet.set_column("D:D", 20)
        format_wrap_text = workbook.add_format({"text_wrap": "true", "bold": "true"})
        worksheet.write("A1", "Warehouse", format_wrap_text)
        worksheet.write("B1", "Product SKU", format_wrap_text)
        worksheet.write("C1", "Inventory Quantity", format_wrap_text)
