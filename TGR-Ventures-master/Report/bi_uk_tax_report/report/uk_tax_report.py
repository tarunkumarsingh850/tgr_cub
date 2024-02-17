from odoo import models
from datetime import datetime


class UKTAXReport(models.AbstractModel):
    _name = "report.bi_uk_tax_report.report_uk_tax_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        ws = workbook.add_worksheet("UK TAX Report")
        boldl = workbook.add_format({"bold": True, "align": "left"})
        boldc = workbook.add_format({"bold": True, "align": "center", "bg_color": "#808080"})
        center = workbook.add_format({"align": "center"})
        right = workbook.add_format({"align": "right"})

        # WIZARD VALUES
        start_date = data["form"]["start_date"]
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = data["form"]["end_date"]
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        tax_type = data["form"]["tax_type"]
        company_id = self.env["res.company"].search([("id", "=", self.env.company.id)])

        ws.merge_range("A1:D2", "UK TAX Report", boldl)
        ws.write("A4", "Company", boldl)
        ws.merge_range("B4:C4", company_id.name, center)
        ws.write("A5", "Start Date", boldl)
        ws.write("A6", "End Date", boldl)
        ws.write("B5", start_date.strftime("%d-%m-%Y"), center)
        ws.write("B6", end_date.strftime("%d-%m-%Y"), center)

        ws.set_column("A:A", 20)
        ws.set_column("B:B", 20)
        ws.set_column("C:C", 20)
        ws.set_column("D:D", 20)
        ws.set_column("E:E", 20)
        ws.set_column("F:F", 20)
        ws.set_column("G:G", 20)

        row = 7

        ws.write("A%s" % row, "Invoice Number", boldc)
        ws.write("B%s" % row, "Date", boldc)
        ws.write("C%s" % row, "Untaxed Amount", boldc)
        ws.write("D%s" % row, "Tax Amount", boldc)
        ws.write("E%s" % row, "Total", boldc)

        row = 8
        taxes = self.env["account.tax"].search([("is_uk_tax", "=", True), ("type_tax_use", "=", tax_type)])
        move_ids = self.env["account.move"].search(
            [
                ("date", ">=", start_date),
                ("date", "<=", end_date),
                ("state", "=", "posted"),
                ("move_type", "!=", "entry"),
            ]
        )

        for record in move_ids:
            tax = self.env["account.move.line"].search([("tax_ids", "in", taxes.ids), ("move_id", "=", record.id)])
            if tax and record.move_type in ("out_invoice", "in_invoice"):
                ws.write("A%s" % row, record.name, center)
                ws.write("B%s" % row, record.date.strftime("%d-%m-%Y"), center)
                ws.write("C%s" % row, record.amount_untaxed, center)
                ws.write("D%s" % row, record.amount_tax, center)
                ws.write("E%s" % row, record.amount_total, center)
                row += 1

        ws.merge_range(f"A{row}:B{row}", "Credit/Debit", boldl)
        row += 1
        for record in move_ids:
            tax = self.env["account.move.line"].search([("tax_ids", "in", taxes.ids), ("move_id", "=", record.id)])
            if tax and record.move_type in ("out_refund", "in_refund"):
                ws.write("A%s" % row, record.name, center)
                ws.write("B%s" % row, record.date.strftime("%d-%m-%Y"), center)
                ws.write("C%s" % row, record.amount_untaxed, center)
                ws.write("D%s" % row, record.amount_tax, center)
                ws.write("E%s" % row, record.amount_total, center)
                row += 1
