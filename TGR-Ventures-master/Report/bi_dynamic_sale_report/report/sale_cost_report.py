from odoo import models


class SaleCostReport(models.AbstractModel):
    _name = "report.bi_dynamic_sale_report.report_sale_cost"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Sales Cost Analysis")
        justify = workbook.add_format({"bottom": True, "top": True, "right": True, "left": True, "font_size": 12})
        justify.set_align("justify")
        bolda = workbook.add_format({"bold": True, "align": "left"})
        boldc = workbook.add_format({"bold": True, "align": "center"})
        center = workbook.add_format({"align": "center"})
        worksheet.merge_range("A1:D1", "Sales Cost Analysis Report", bolda)

        partner_id = self.env["res.partner"].search([("id", "=", data["form"]["partner_id"])])
        worksheet.write("A3", "Company", bolda)
        worksheet.write("A4", "Customer", bolda)
        worksheet.merge_range("B3:D3", self.env.user.company_id.name, center)
        worksheet.merge_range("B4:D4", partner_id.name if partner_id else "", center)

        worksheet.write("F3", "Start Date", bolda)
        worksheet.write("F4", "End Date", bolda)
        worksheet.write("G3", data["form"]["date_from"], center)
        worksheet.write("G4", data["form"]["date_to"], center)

        row = 6
        new_row = row + 1
        worksheet.set_column("A:A", 10)
        worksheet.set_column("B:B", 15)
        worksheet.set_column("C:C", 15)
        worksheet.set_column("D:D", 15)
        worksheet.set_column("E:E", 15)
        worksheet.set_column("F:F", 15)
        worksheet.set_column("G:G", 25)
        worksheet.set_column("H:H", 18)
        worksheet.set_column("I:I", 15)
        worksheet.set_column("J:J", 15)
        worksheet.set_column("K:K", 15)
        worksheet.set_column("L:L", 15)
        worksheet.set_column("M:M", 15)

        worksheet.write("A%s" % row, "Order", boldc)
        worksheet.write("B%s" % row, "Product", boldc)
        worksheet.write("C%s" % row, "Qty", boldc)
        worksheet.write("D%s" % row, "Sales Price", boldc)
        worksheet.write("E%s" % row, "Cost", boldc)

        domain = []
        if data["form"]["date_from"]:
            domain.append(("date_order", ">=", data["form"]["date_from"]))
        if data["form"]["date_to"]:
            domain.append(("date_order", "<=", data["form"]["date_to"]))
        if data["form"]["partner_id"]:
            domain.append(("partner_id", "=", data["form"]["partner_id"]))
        record = self.env["sale.order"].search(domain)
        for line in record.order_line:
            if line.product_id.detailed_type == "product":
                worksheet.write("A%s" % new_row, line.order_id.name, center)
                worksheet.write("B%s" % new_row, line.product_id.default_code, center)
                worksheet.write("C%s" % new_row, line.product_uom_qty, center)
                worksheet.write("D%s" % new_row, line.product_id.lst_price, center)
                cost = 0
                additional_cost = 0
                if data["form"]["cost_percentage"]:
                    cost = (line.product_id.standard_price * data["form"]["cost_percentage"]) / 100
                    additional_cost = cost + line.product_id.standard_price
                worksheet.write("E%s" % new_row, round(additional_cost, 2), center)
                new_row += 1
