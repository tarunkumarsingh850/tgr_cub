from odoo import models
import string


class ExportemplateProductWebsiteExport(models.AbstractModel):
    _name = "report.bi_export_product_enable_website.export_product_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Export Template"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Product Website Template")
        heading_format = workbook.add_format(
            {
                "bold": 1,
                "bottom": True,
                "right": True,
                "left": True,
                "top": True,
                "align": "Center",
                "font_size": "12",
                "border_color": "#000000",
            }
        )
        content_format = workbook.add_format(
            {
                "bottom": True,
                "right": True,
                "left": True,
                "top": True,
                "align": "Center",
                "font_size": "12",
                "border_color": "#000000",
            }
        )
        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 15)
        worksheet.set_column("D:D", 15)
        worksheet.set_column("E:E", 15)
        worksheet.set_column("F:F", 15)
        worksheet.set_column("G:G", 15)
        worksheet.set_column("H:H", 15)
        worksheet.set_column("I:I", 15)
        worksheet.set_column("J:J", 15)
        worksheet.set_column("K:K", 15)
        worksheet.set_column("L:L", 15)
        worksheet.set_column("M:M", 15)
        worksheet.set_column("N:N", 15)
        worksheet.set_column("O:O", 15)
        worksheet.set_column("P:P", 20)
        worksheet.set_column("Q:Q", 15)
        worksheet.set_column("R:R", 15)
        worksheet.set_column("S:S", 15)
        worksheet.set_column("T:T", 15)
        worksheet.set_column("U:U", 15)
        worksheet.set_column("V:V", 15)

        alphabets = list(string.ascii_uppercase)
        letters = list(string.ascii_uppercase)
        for a in alphabets:
            for b in alphabets:
                letters.append("{}{}".format(a, b))
        col = 19

        worksheet.write("A1", "Product Name", heading_format)
        worksheet.write("B1", "SKU", heading_format)
        worksheet.write("C1", "UK Tiger One", heading_format)
        worksheet.write("D1", "EU Tiger One", heading_format)
        worksheet.write("E1", "SA Tiger One", heading_format)
        worksheet.write("F1", "USA Tiger One", heading_format)
        worksheet.write("G1", "UK Seedsman", heading_format)
        worksheet.write("H1", "EU Seedsman ", heading_format)
        worksheet.write("I1", "SA Seedsman ", heading_format)
        worksheet.write("J1", "USA Seedsman ", heading_format)
        worksheet.write("K1", "UK Eztestkits ", heading_format)
        worksheet.write("L1", "EU Eztestkits ", heading_format)
        worksheet.write("M1", "SA Eztestkits ", heading_format)
        worksheet.write("N1", "USA Eztestkits ", heading_format)
        worksheet.write("O1", "Pytho N ", heading_format)
        worksheet.write("P1", "Product Visibility", heading_format)
        worksheet.write("Q1", "Description", heading_format)
        worksheet.write("R1", "Category", heading_format)
        worksheet.write("S1", "Product Brand", heading_format)
        magento_attribute_ids = self.env["magento.attribute"].search([])
        for attribute_id in magento_attribute_ids:
            worksheet.write(f"{letters[col]}1", attribute_id.name, heading_format)
            col += 1

        magento_website = data["form"]["magento_website_id"]
        website = self.env["magento.website"].search([("id", "=", magento_website)])
        products = self.env["magento.product.configurable"].search([], limit=3)
        row = 2
        if products:
            for product_id in products:
                worksheet.write(
                    "A%s" % row,
                    product_id.magento_product_name if product_id.magento_product_name else "",
                    content_format,
                )
                worksheet.write("B%s" % row, product_id.magento_sku if product_id.magento_sku else "", content_format)
                worksheet.write(
                    "C%s" % row,
                    product_id.uk_tiger_one_boolean if product_id.uk_tiger_one_boolean else "",
                    content_format,
                )
                worksheet.write(
                    "D%s" % row,
                    product_id.eu_tiger_one_boolean if product_id.eu_tiger_one_boolean else "",
                    content_format,
                )
                worksheet.write(
                    "E%s" % row,
                    product_id.sa_tiger_one_boolean if product_id.sa_tiger_one_boolean else "",
                    content_format,
                )
                worksheet.write(
                    "F%s" % row,
                    product_id.usa_tiger_one_boolean if product_id.usa_tiger_one_boolean else "",
                    content_format,
                )
                worksheet.write(
                    "G%s" % row,
                    product_id.uk_seedsman_boolean if product_id.uk_seedsman_boolean else "",
                    content_format,
                )
                worksheet.write(
                    "H%s" % row,
                    product_id.eu_seedsman_boolean if product_id.eu_seedsman_boolean else "",
                    content_format,
                )
                worksheet.write(
                    "I%s" % row,
                    product_id.sa_seedsman_boolean if product_id.sa_seedsman_boolean else "",
                    content_format,
                )
                worksheet.write(
                    "J%s" % row,
                    product_id.usa_seedsman_boolean if product_id.usa_seedsman_boolean else "",
                    content_format,
                )
                worksheet.write(
                    "K%s" % row,
                    product_id.uk_eztestkits_boolean if product_id.uk_eztestkits_boolean else "",
                    content_format,
                )
                worksheet.write(
                    "L%s" % row,
                    product_id.eu_eztestkits_boolean if product_id.eu_eztestkits_boolean else "",
                    content_format,
                )
                worksheet.write(
                    "M%s" % row,
                    product_id.sa_eztestkits_boolean if product_id.sa_eztestkits_boolean else "",
                    content_format,
                )
                worksheet.write(
                    "N%s" % row,
                    product_id.usa_eztestkits_boolean if product_id.usa_eztestkits_boolean else "",
                    content_format,
                )
                worksheet.write(
                    "O%s" % row, product_id.pytho_n_boolean if product_id.pytho_n_boolean else "", content_format
                )
                worksheet.write(
                    "P%s" % row, product_id.product_visibility if product_id.product_visibility else "", content_format
                )
                worksheet.write("Q%s" % row, product_id.description if product_id.description else "", content_format)
                worksheet.write("R%s" % row, product_id.categ_id.name if product_id.categ_id else "", content_format)
                worksheet.write(
                    "S%s" % row, product_id.brand_id.breeder_name if product_id.brand_id else "", content_format
                )
                row += 1
