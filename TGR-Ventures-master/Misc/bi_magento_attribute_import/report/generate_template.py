from odoo import models
import string


class UpdateMagentoAttributes(models.AbstractModel):
    _name = "report.bi_magento_attribute_import.generate_template_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Export Template Line Import"

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
        format_wrap_text = workbook.add_format({"text_wrap": "true"})
        worksheet.write("A1", "Product SKU", format_wrap_text)
        alphabets = list(string.ascii_uppercase)
        letters = list(string.ascii_uppercase)
        for a in alphabets:
            for b in alphabets:
                letters.append("{}{}".format(a, b))
        col = 1
        magento_attribute_ids = self.env["magento.attribute"].search([])
        for attribute_id in magento_attribute_ids:
            worksheet.write(f"{letters[col]}1", attribute_id.name, format_wrap_text)
            col += 1
