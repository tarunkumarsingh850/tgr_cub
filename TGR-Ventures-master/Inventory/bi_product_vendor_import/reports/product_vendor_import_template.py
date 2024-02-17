from odoo import models


class ProductVendorImportTemplate(models.AbstractModel):
    _name = "report.bi_product_vendor_import.product_vendor_import_template"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet()
        sheet.set_column("A:A", 30)
        sheet.set_column("B:B", 30)
        sheet.set_column("C:C", 30)
        sheet.set_column("D:D", 30)
        sheet.set_column("E:E", 30)
        sheet.set_column("F:F", 30)
        header = workbook.add_format({"bold": True, "align": "center"})
        sheet.write("A1", "SKU", header)
        sheet.write("B1", "Vendor", header)
        sheet.write("C1", "Currency", header)
        sheet.write("D1", "Quantity", header)
        sheet.write("E1", "Price", header)
        sheet.write("F1", "Delivery Lead Time", header)
