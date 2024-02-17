# See LICENSE file for full copyright and licensing details.
from odoo import models


class ReportSale(models.AbstractModel):
    _name = "report.bi_product_company_wise_report.product_report"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        brand_id = lines.product_breeder_id
        company_id = lines.company_id
        categ_id = lines.categ_id

        worksheet = workbook.add_worksheet("Product Report")
        format1 = workbook.add_format({"font_size": 12, "align": "center", "bold": True})
        format3 = workbook.add_format({"font_size": 10})
        font_size_8 = workbook.add_format({"bottom": True, "top": True, "right": True, "left": True, "font_size": 8})
        justify = workbook.add_format({"bottom": True, "top": True, "right": True, "left": True, "font_size": 12})
        format3.set_align("center")
        font_size_8.set_align("center")
        justify.set_align("justify")
        format1.set_align("center")
        worksheet.set_column("A:A", 30)
        worksheet.set_column("B:B", 30)
        worksheet.set_column("C:C", 30)
        worksheet.set_column("D:D", 30)
        worksheet.set_column("E:E", 30)
        worksheet.set_column("F:F", 30)
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

        worksheet.write("A1", "Brand Description", format1)
        worksheet.write("B1", "SKU", format1)
        worksheet.write("C1", "Product Name", format1)
        worksheet.write("D1", "Pack Size Description", format1)
        worksheet.write("E1", "Flower Type Description", format1)
        worksheet.write("F1", "Sex Description", format1)
        worksheet.write("G1", "Last Cost", format1)
        if company_id.id == 10:
            worksheet.write("H1", "Retail Default EUR", format1)
            worksheet.write("I1", "Wsale Default EUR", format1)
            worksheet.write("J1", "BULES/Stock", format1)
            worksheet.write("K1", "BULUK/Stock", format1)
            worksheet.write("L1", "ESCDO/Stock", format1)
            worksheet.write("M1", "WSALE/Stock", format1)
            worksheet.write("N1", "LOST/Stock", format1)
            worksheet.write("O1", "MALAG/Stock", format1)
            worksheet.write("P1", "UK3PL/Stock", format1)
            worksheet.write("Q1", "UKBAR/Stock", format1)
            worksheet.write("R1", "UKCDO/Stock", format1)
            worksheet.write("S1", "UKWSA/Stock", format1)
            worksheet.write("T1", "USIT/Stock", format1)
            worksheet.write("U1", "ZACDO/Stock", format1)
            worksheet.write("V1", "ZATES/Stock", format1)
            worksheet.write("W1", "ZAWSA/Stock", format1)
        if company_id.id == 11:
            worksheet.write("H1", "Retail USD", format1)
            worksheet.write("I1", "Wsale USD", format1)
            worksheet.write("J1", "LIVE/Stock", format1)
            worksheet.write("K1", "WHUSA/Stock", format1)
            worksheet.write("L1", "UNPAC/Stock", format1)
            worksheet.write("M1", "CODUS/Stock", format1)

        product_details = lines.get_product_details(brand_id, categ_id)

        live_stock = 0
        codus_stock = 0
        whusa_stock = 0
        unpac_stock = 0
        bules_stock = 0
        buluk_stock = 0
        escdo_stock = 0
        wsale_stock = 0
        lost_stock = 0
        malag_stock = 0
        uk3pl_stock = 0
        ukbar_stock = 0
        ukcdo_stock = 0
        ukwsa_stock = 0
        usit_stock = 0
        zacdo_stock = 0
        zates_stock = 0
        zawsa_stock = 0

        row = 2
        for product in product_details:
            worksheet.write("A%s" % row, product.product_tmpl_id.product_breeder_id.breeder_name, format3)
            worksheet.write("B%s" % row, product.product_tmpl_id.default_code, format3)
            worksheet.write("C%s" % row, product.product_tmpl_id.name, format3)
            worksheet.write("D%s" % row, product.product_tmpl_id.pack_size_desc, format3)
            worksheet.write("E%s" % row, product.product_tmpl_id.flower_type_id.flower_type_des, format3)
            worksheet.write("F%s" % row, product.product_tmpl_id.product_sex_id.product_sex_des, format3)
            worksheet.write("G%s" % row, product.product_tmpl_id.standard_price, format3)
            if company_id.id == 10:
                worksheet.write("H%s" % row, product.product_tmpl_id.retail_default_price, format3)
                worksheet.write("I%s" % row, product.product_tmpl_id.wholesale_price_value, format3)

                if self.env["stock.location"].search([("id", "=", 156)]):
                    bules_stock = product.with_context({"location": 156}).qty_available or 0.00
                if self.env["stock.location"].search([("id", "=", 162)]):
                    buluk_stock = product.with_context({"location": 162}).qty_available or 0.00
                if self.env["stock.location"].search([("id", "=", 364)]):
                    escdo_stock = product.with_context({"location": 364}).qty_available or 0.00
                if self.env["stock.location"].search([("id", "=", 168)]):
                    wsale_stock = product.with_context({"location": 168}).qty_available or 0.00

                if self.env["stock.location"].search([("id", "=", 180)]):
                    lost_stock = product.with_context({"location": 180}).qty_available or 0.00
                if self.env["stock.location"].search([("id", "=", 144)]):
                    malag_stock = product.with_context({"location": 144}).qty_available or 0.00
                if self.env["stock.location"].search([("id", "=", 138)]):
                    uk3pl_stock = product.with_context({"location": 138}).qty_available or 0.00
                if self.env["stock.location"].search([("id", "=", 132)]):
                    ukbar_stock = product.with_context({"location": 132}).qty_available or 0.00
                if self.env["stock.location"].search([("id", "=", 346)]):
                    ukcdo_stock = product.with_context({"location": 346}).qty_available or 0.00
                if self.env["stock.location"].search([("id", "=", 298)]):
                    ukwsa_stock = product.with_context({"location": 298}).qty_available or 0.00
                if self.env["stock.location"].search([("id", "=", 174)]):
                    usit_stock = product.with_context({"location": 174}).qty_available or 0.00
                if self.env["stock.location"].search([("id", "=", 352)]):
                    zacdo_stock = product.with_context({"location": 352}).qty_available or 0.00
                if self.env["stock.location"].search([("id", "=", 150)]):
                    zates_stock = product.with_context({"location": 150}).qty_available or 0.00
                if self.env["stock.location"].search([("id", "=", 358)]):
                    zawsa_stock = product.with_context({"location": 358}).qty_available or 0.00

                worksheet.write("J%s" % row, bules_stock, format3)
                worksheet.write("K%s" % row, buluk_stock, format3)
                worksheet.write("L%s" % row, escdo_stock, format3)
                worksheet.write("M%s" % row, wsale_stock, format3)
                worksheet.write("N%s" % row, lost_stock, format3)
                worksheet.write("O%s" % row, malag_stock, format3)
                worksheet.write("P%s" % row, uk3pl_stock, format3)
                worksheet.write("Q%s" % row, ukbar_stock, format3)
                worksheet.write("R%s" % row, ukcdo_stock, format3)
                worksheet.write("S%s" % row, ukwsa_stock, format3)
                worksheet.write("T%s" % row, usit_stock, format3)
                worksheet.write("U%s" % row, zacdo_stock, format3)
                worksheet.write("V%s" % row, zates_stock, format3)
                worksheet.write("W%s" % row, zawsa_stock, format3)
                row += 1

            if company_id.id == 11:
                worksheet.write("H%s" % row, product.product_tmpl_id.retail_us_price, format3)
                worksheet.write("I%s" % row, product.product_tmpl_id.wholesale_us, format3)

                if self.env["stock.location"].search([("id", "=", 190)]):
                    live_stock = product.with_context({"location": 190}).qty_available
                if self.env["stock.location"].search([("id", "=", 196)]):
                    whusa_stock = product.with_context({"location": 196}).qty_available
                if self.env["stock.location"].search([("id", "=", 202)]):
                    unpac_stock = product.with_context({"location": 202}).qty_available
                if self.env["stock.location"].search([("id", "=", 292)]):
                    codus_stock = product.with_context({"location": 292}).qty_available

                worksheet.write("J%s" % row, live_stock, format3)
                worksheet.write("K%s" % row, whusa_stock, format3)
                worksheet.write("L%s" % row, unpac_stock, format3)
                worksheet.write("M%s" % row, codus_stock, format3)
                row += 1
