from odoo import models


class ExportemplateTransactionImport(models.AbstractModel):
    _name = "report.bi_import_account_bank_statement.export_template_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Export Template Line Import"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Import Transaction Template")
        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 20)
        worksheet.set_column("D:D", 20)
        format_wrap_text = workbook.add_format({"text_wrap": "true"})
        worksheet.write("A1", "Date", format_wrap_text)
        worksheet.write("B1", "Label", format_wrap_text)
        worksheet.write("C1", "Partner", format_wrap_text)
        worksheet.write("D1", "Amount", format_wrap_text)
