from odoo import models


class ExportemplateShippingImport(models.AbstractModel):
    _name = "report.bi_shipping_update_report.export_template_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Export Template"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Shipping Template")
        heading_format = workbook.add_format(
            {
                "bold": 1,
                "bottom": True,
                "right": True,
                "left": True,
                "top": True,
                "align": "left",
                "color": "#000000",
                "font_size": "12",
                "border_color": "#000000",
                "bg_color": "#808080",
            }
        )
        checktrue_format = workbook.add_format(
            {
                "bold": 1,
                "bottom": True,
                "right": True,
                "left": True,
                "top": True,
                "align": "Center",
                "font_size": "10",
                "border_color": "#000000",
            }
        )
        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:B", 20)
        worksheet.write("A1", "Reference", heading_format)
        worksheet.write("B1", "Source Document", heading_format)
        worksheet.write("C1", "Tracking Reference", heading_format)
        stock_ids = data["form"]["ids"]

        stocks = self.env["stock.picking"].search([("id", "in", stock_ids)])
        row = 2
        for stock_id in stocks:
            worksheet.write("A%s" % row, stock_id.name if stock_id.name else "", checktrue_format)
            worksheet.write("B%s" % row, stock_id.origin if stock_id.origin else "", checktrue_format)
            worksheet.write(
                "C%s" % row, stock_id.carrier_tracking_ref if stock_id.carrier_tracking_ref else "", checktrue_format
            )
            row += 1
