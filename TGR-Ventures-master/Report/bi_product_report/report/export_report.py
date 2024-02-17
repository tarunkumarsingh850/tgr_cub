from odoo import models
import datetime


class ExportReport(models.AbstractModel):
    _name = "report.bi_product_report.export_report_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Export Report"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Product Report")
        worksheet.set_column("A:A", 25)
        worksheet.set_column("B:B", 30)
        worksheet.set_column("C:C", 20)
        worksheet.set_column("D:D", 20)
        worksheet.set_column("E:E", 20)
        format_wrap_text = workbook.add_format(
            {
                "bottom": True,
                "top": True,
                "right": True,
                "left": True,
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_size": 11,
            }
        )
        format4 = workbook.add_format(
            {
                "bottom": True,
                "top": True,
                "right": True,
                "left": True,
                "valign": "vcenter",
                "font_size": 11,
            }
        )

        worksheet.write("A1", "SKU CODE", format_wrap_text)
        worksheet.write("B1", "PRODUCT", format_wrap_text)
        worksheet.write("C1", "ON HAND QUANTITY", format_wrap_text)
        worksheet.write("D1", "Available Quantity", format_wrap_text)
        worksheet.write("E1", "LOCATION", format_wrap_text)

        product = self.env["product.product"].browse(data["form"]["product"])
        warehouse_id = self.env["stock.warehouse"].browse(data["form"]["warehouse_id"])
        location_id = self.env["stock.location"].search(
            [("complete_name", "=", warehouse_id.lot_stock_id.complete_name)]
        )
        self.env["stock.location"].search([("usage", "in", ["internal", "transit"])])
        row = 2
        for each in product:
            for location in location_id:
                opening_qty = each.with_context(
                    {"location": location.id, "to_date": datetime.datetime.now()}
                ).qty_available
                if opening_qty:
                    worksheet.write("C%s" % row, opening_qty, format4)
            worksheet.write("A%s" % row, each.default_code, format4)
            worksheet.write("B%s" % row, each.name, format4)
            worksheet.write("E%s" % row, location_id.complete_name, format4)
            available_qty = each.with_context({"location": location_id.id}).sudo().free_qty
            worksheet.write("D%s" % row, available_qty, format4)
            row += 1
