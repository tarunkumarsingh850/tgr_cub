from odoo import models


class ExportemplateProductImport(models.AbstractModel):
    _name = "report.bi_export_products.export_template_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Export Template"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Product Template")
        heading_format = workbook.add_format(
            {
                "bold": 1,
                "bottom": True,
                "right": True,
                "left": True,
                "top": True,
                "align": "Center",
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
                "color": "#0096FF",
                "font_size": "10",
                "border_color": "#000000",
            }
        )
        black_format = workbook.add_format(
            {
                "bold": 1,
                "bottom": True,
                "right": True,
                "left": True,
                "top": True,
                "align": "Center",
                "color": "#000000",
                "font_size": "10",
                "border_color": "#000000",
            }
        )
        checkfalse_format = workbook.add_format(
            {
                "bold": 1,
                "bottom": True,
                "right": True,
                "left": True,
                "top": True,
                "align": "Center",
                "color": "#FF0000",
                "font_size": "10",
                "border_color": "#000000",
            }
        )

        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 20)
        worksheet.set_column("D:D", 20)
        worksheet.set_column("E:E", 20)
        worksheet.set_column("F:F", 20)
        worksheet.set_column("G:G", 20)
        worksheet.set_column("H:H", 20)
        worksheet.set_column("I:I", 20)
        worksheet.write("A1", "Product Name", heading_format)
        worksheet.write("B1", "SKU", heading_format)
        worksheet.write("C1", "Brand", heading_format)
        worksheet.write("D1", "Responsible", heading_format)
        worksheet.write("E1", "Sale Price", heading_format)
        worksheet.write("F1", "Cost", heading_format)
        worksheet.write("G1", "Quantity On Hand", heading_format)
        worksheet.write("H1", "Forecasted Quantity", heading_format)
        worksheet.write("I1", "Unit OF Measure", heading_format)
        product_ids = data["form"]["ids"]

        products = self.env["product.template"].search([("id", "in", product_ids)])
        row = 2
        for product_id in products:
            if product_id.check_color:
                worksheet.write("A%s" % row, product_id.name if product_id.name else "", checktrue_format)
                worksheet.write(
                    "B%s" % row, product_id.default_code if product_id.default_code else "", checktrue_format
                )
                worksheet.write(
                    "C%s" % row,
                    product_id.product_breeder_id.breeder_name if product_id.product_breeder_id else "",
                    checktrue_format,
                )
                worksheet.write(
                    "D%s" % row, product_id.responsible_id.name if product_id.responsible_id else "", checktrue_format
                )
                worksheet.write("E%s" % row, product_id.list_price if product_id.list_price else "", checktrue_format)
                worksheet.write(
                    "F%s" % row, product_id.standard_price if product_id.standard_price else "", checktrue_format
                )
                worksheet.write(
                    "G%s" % row, product_id.qty_available if product_id.qty_available else "", checktrue_format
                )
                worksheet.write(
                    "H%s" % row, product_id.virtual_available if product_id.virtual_available else "", checktrue_format
                )
                worksheet.write("I%s" % row, product_id.uom_id.name if product_id.uom_id else "", checktrue_format)
            elif product_id.black_color:
                worksheet.write("A%s" % row, product_id.name if product_id.name else "", black_format)
                worksheet.write("B%s" % row, product_id.default_code if product_id.default_code else "", black_format)
                worksheet.write(
                    "C%s" % row,
                    product_id.product_breeder_id.breeder_name if product_id.product_breeder_id else "",
                    black_format,
                )
                worksheet.write(
                    "D%s" % row, product_id.responsible_id.name if product_id.responsible_id else "", black_format
                )
                worksheet.write("E%s" % row, product_id.list_price if product_id.list_price else "", black_format)
                worksheet.write(
                    "F%s" % row, product_id.standard_price if product_id.standard_price else "", black_format
                )
                worksheet.write("G%s" % row, product_id.qty_available if product_id.qty_available else "", black_format)
                worksheet.write(
                    "H%s" % row, product_id.virtual_available if product_id.virtual_available else "", black_format
                )
                worksheet.write("I%s" % row, product_id.uom_id.name if product_id.uom_id else "", black_format)
            elif not product_id.check_color:
                worksheet.write("A%s" % row, product_id.name if product_id.name else "", checkfalse_format)
                worksheet.write(
                    "B%s" % row, product_id.default_code if product_id.default_code else "", checkfalse_format
                )
                worksheet.write(
                    "C%s" % row,
                    product_id.product_breeder_id.breeder_name if product_id.product_breeder_id else "",
                    checkfalse_format,
                )
                worksheet.write(
                    "D%s" % row, product_id.responsible_id.name if product_id.responsible_id else "", checkfalse_format
                )
                worksheet.write("E%s" % row, product_id.list_price if product_id.list_price else "", checkfalse_format)
                worksheet.write(
                    "F%s" % row, product_id.standard_price if product_id.standard_price else "", checkfalse_format
                )
                worksheet.write(
                    "G%s" % row, product_id.qty_available if product_id.qty_available else "", checkfalse_format
                )
                worksheet.write(
                    "H%s" % row, product_id.virtual_available if product_id.virtual_available else "", checkfalse_format
                )
                worksheet.write("I%s" % row, product_id.uom_id.name if product_id.uom_id else "", checkfalse_format)
            row += 1
