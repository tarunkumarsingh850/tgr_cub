from odoo import models
from datetime import datetime

# from cStringIO import StringIO


class AccountingReport(models.AbstractModel):
    _name = "report.bi_369_report.generate_369_report_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        ws = workbook.add_worksheet("369 Summary Report")
        boldl = workbook.add_format({"bold": True, "align": "left"})
        boldc = workbook.add_format({"bold": True, "align": "center", "bg_color": "#808080"})
        center = workbook.add_format({"align": "center"})
        right = workbook.add_format({"align": "right"})

        # WIZARD VALUES
        start_date = data["form"]["start_date"]
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = data["form"]["end_date"]
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        company_id = self.env["res.company"].search([("id", "=", self.env.company.id)])

        ws.merge_range("A1:D1", "369 Summary Report", boldl)
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

        ws.write("A%s" % row, "Country code ", boldc)
        ws.write("B%s" % row, "Country", boldc)
        ws.write("C%s" % row, "Vat Rate", boldc)
        ws.write("D%s" % row, "Taxable Base", boldc)
        ws.write("E%s" % row, "Tax Amount", boldc)
        ws.write("F%s" % row, "Amount Total", boldc)

        row = 8
        eu_country_codes = self.env.ref("base.europe").country_ids.mapped("code")
        eu_country_codes.remove("ES")

        account_tag_id = self.env["account.account.tag"].search([("name", "=", "OSS")])
        for country_code in eu_country_codes:

            tax = (
                self.env["account.move.line"]
                .search(
                    [
                        ("move_id.invoice_date", ">=", start_date),
                        ("move_id.invoice_date", "<=", end_date),
                        ("company_id", "=", company_id.id),
                        ("parent_state", "=", "posted"),
                        ("tax_tag_ids", "in", account_tag_id.ids),
                        ("move_id.move_type", "=", "out_invoice"),
                        # ('move_id.partner_id.country_id.code','=',country_code)
                    ],
                    limit=1,
                )
                .mapped("tax_ids")
            )

            move_ids = (
                self.env["account.move.line"]
                .search(
                    [
                        ("move_id.invoice_date", ">=", start_date),
                        ("move_id.invoice_date", "<=", end_date),
                        ("company_id", "=", company_id.id),
                        ("parent_state", "=", "posted"),
                        ("move_id.move_type", "=", "out_invoice"),
                        ("tax_tag_ids", "in", account_tag_id.ids),
                        # ('move_id.partner_id.country_id.code','=',country_code)
                    ]
                )
                .mapped("move_id")
            )
            untaxed_amount = 0
            amount_tax = 0
            amount_total = 0
            for record in move_ids:
                # if record.invoice_line_ids and record.invoice_line_ids.tax_ids and any(record.invoice_line_ids.tax_ids.mapped('custom_country_id')):
                if record.invoice_line_ids[0].tax_ids[0].mapped("custom_country_id").code in [country_code]:
                    untaxed_amount += record.amount_untaxed
                    amount_tax += record.amount_tax
                    amount_total += record.amount_total

            if amount_total != 0:
                # if
                country_id = self.env["res.country"].search([("code", "=", country_code)], limit=1)
                ws.write("A%s" % row, country_code, center)
                ws.write("B%s" % row, country_id.name if country_id else "", center)
                ws.write("C%s" % row, record.invoice_line_ids[0].tax_ids[0].name if tax else "", center)
                ws.write("D%s" % row, round(untaxed_amount, 2), right)
                ws.write("E%s" % row, round(amount_tax, 2), right)
                ws.write("F%s" % row, round(amount_total, 2), right)
                row += 1
        row += 1
        ws.merge_range(f"A{row}:D{row}", "Credit Notes", boldl)
        row += 1
        for country_code in eu_country_codes:
            tax = (
                self.env["account.move.line"]
                .search(
                    [
                        ("move_id.invoice_date", ">=", start_date),
                        ("move_id.invoice_date", "<=", end_date),
                        ("company_id", "=", company_id.id),
                        ("parent_state", "=", "posted"),
                        ("tax_tag_ids", "in", account_tag_id.ids),
                        ("move_id.move_type", "=", "out_refund"),
                        # ('move_id.partner_id.country_id.code','=',country_code)
                    ],
                    limit=1,
                )
                .mapped("tax_ids")
            )

            move_ids = (
                self.env["account.move.line"]
                .search(
                    [
                        ("move_id.invoice_date", ">=", start_date),
                        ("move_id.invoice_date", "<=", end_date),
                        ("company_id", "=", company_id.id),
                        ("parent_state", "=", "posted"),
                        ("move_id.move_type", "=", "out_refund"),
                        ("tax_tag_ids", "in", account_tag_id.ids),
                        # ('move_id.partner_id.country_id.code','=',country_code)
                    ]
                )
                .mapped("move_id")
            )
            untaxed_amount = 0
            amount_tax = 0
            amount_total = 0
            for record in move_ids:
                if record.invoice_line_ids.tax_ids:
                    if record.invoice_line_ids[0].tax_ids[0].mapped("custom_country_id").code in [country_code]:
                        untaxed_amount += record.amount_untaxed
                        amount_tax += record.amount_tax
                        amount_total += record.amount_total

            if amount_total != 0:
                country_id = self.env["res.country"].search([("code", "=", country_code)], limit=1)
                ws.write("A%s" % row, country_code, center)
                ws.write("B%s" % row, country_id.name if country_id else "", center)
                ws.write("C%s" % row, tax.name if tax else "", center)
                ws.write("D%s" % row, round(untaxed_amount, 2), right)
                ws.write("E%s" % row, round(amount_tax, 2), right)
                ws.write("F%s" % row, round(amount_total, 2), right)
                row += 1

        ws2 = workbook.add_worksheet("369 Split UP Report")

        ws2.set_column("A:A", 20)
        ws2.set_column("B:B", 20)
        ws2.set_column("C:C", 20)
        ws2.set_column("D:D", 20)
        ws2.set_column("E:E", 20)
        ws2.set_column("F:F", 20)
        ws2.set_column("G:G", 20)

        row = 1

        ws2.write("A%s" % row, "Invoice Number ", boldc)
        ws2.write("B%s" % row, "Customer", boldc)
        ws2.write("C%s" % row, "Date", boldc)
        ws2.write("D%s" % row, "Vat Rate", boldc)
        ws2.write("E%s" % row, "Taxable Base", boldc)
        ws2.write("F%s" % row, "Tax Amount", boldc)
        ws2.write("G%s" % row, "Amount Total", boldc)

        row = 2

        for country_code in eu_country_codes:
            set_country = 0
            invoice_ids = self.env["account.move"].search(
                [
                    ("invoice_date", ">=", start_date),
                    ("invoice_date", "<=", end_date),
                    ("company_id", "=", company_id.id),
                    ("state", "=", "posted"),
                    ("move_type", "=", "out_invoice"),
                ]
            )
            for record in invoice_ids:
                move_ids = self.env["account.move.line"].search(
                    [("tax_tag_ids", "in", account_tag_id.ids), ("move_id", "=", record.id)]
                )
                if move_ids:
                    if record.invoice_line_ids[0].tax_ids[0].mapped("custom_country_id").code in [country_code]:
                        if record.amount_total != 0:
                            if set_country == 0:
                                country_id = self.env["res.country"].search([("code", "=", country_code)], limit=1)
                                country_name = country_code + ":" + country_id.name
                                ws2.merge_range(f"A{row}:B{row}", country_name, boldl)
                                row += 1
                                set_country = 1
                            ws2.write("A%s" % row, record.name, center)
                            ws2.write("B%s" % row, record.partner_id.name, center)
                            ws2.write("C%s" % row, record.date.strftime("%d-%m-%Y"), center)
                            for tax in move_ids.mapped("tax_ids"):
                                ws2.write("D%s" % row, tax.name if tax else "", center)
                            ws2.write("E%s" % row, round(record.amount_untaxed, 2), right)
                            ws2.write("F%s" % row, round(record.amount_tax, 2), right)
                            ws2.write("G%s" % row, round(record.amount_total, 2), right)
                            row += 1
