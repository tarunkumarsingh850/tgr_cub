from odoo import models


class IntrastatReport(models.AbstractModel):
    _name = "report.bi_intrastat_report.intrastat_report_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Intrastat Report"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Intrastat Report")
        worksheet.set_column("A:A", 25)
        worksheet.set_column("B:B", 30)
        worksheet.set_column("C:C", 20)
        worksheet.set_column("D:D", 20)
        worksheet.set_column("E:E", 20)
        worksheet.set_column("F:F", 30)
        worksheet.set_column("G:G", 20)
        worksheet.set_column("H:H", 20)
        worksheet.set_column("I:I", 20)
        format_wrap_text = workbook.add_format(
            {
                "bottom": True,
                "top": True,
                "right": True,
                "left": True,
                "bold": True,
                "align": "left",
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
        format_number = workbook.add_format(
            {
                "bottom": True,
                "top": True,
                "right": True,
                "left": True,
                "align": "right",
                "valign": "vcenter",
                "font_size": 11,
            }
        )

        worksheet.write("A1", "Invoice Number", format_wrap_text)
        worksheet.write("B1", "Country Code", format_wrap_text)
        worksheet.write("C1", "Type", format_wrap_text)
        worksheet.write("D1", "Partner", format_wrap_text)
        worksheet.write("E1", "Ref", format_wrap_text)
        worksheet.write("F1", "Partner VAT", format_wrap_text)
        worksheet.write("G1", "Weight", format_wrap_text)
        worksheet.write("H1", "Value", format_wrap_text)
        worksheet.write("I1", "Unit", format_wrap_text)
        worksheet.write("J1", "Pack Size", format_wrap_text)
        worksheet.write("K1", "Total Quantity", format_wrap_text)
        eu_country_codes = self.env.ref("base.europe").country_ids.mapped("code")
        account_tag_id = self.env["account.account.tag"].search([("is_intrastat", "=", True)])
        tax_ids = self.env["account.tax"].search([("is_intrastat", "=", True)])

        row = 2

        if data["form"]["move_type"]:
            domain = []
            domain.append(("date", ">=", data["form"]["date_start"]))
            domain.append(("date", "<=", data["form"]["date_end"]))
            domain.append(("move_id.partner_id.country_id.code", "!=", "ES"))
            domain.append(("move_id.partner_id.country_id.code", "in", eu_country_codes))
            domain.append(("parent_state", "=", "posted"))
            domain.append(("move_id.edi_state", "=", "sent"))
            if data["form"]["move_type"]:
                if data["form"]["move_type"] == "dispatch":
                    move_type = "out_invoice"
                    domain.append(("tax_tag_ids", "in", account_tag_id.ids))
                elif data["form"]["move_type"] == "arrival":
                    move_type = "in_invoice"
                    domain.append(("tax_ids", "in", tax_ids.ids))
                domain.append(("move_id.move_type", "=", move_type))
            invoices = self.env["account.move.line"].search(domain).mapped("move_id")

            for each in invoices:
                worksheet.write("A%s" % row, each.name if each.name else "", format4)
                worksheet.write(
                    "B%s" % row, each.partner_id.country_id.name if each.partner_id.country_id else "", format4
                )
                if each.move_type == "out_invoice":
                    move_type = "Dispatch"
                elif each.move_type == "in_invoice":
                    move_type = "Arrival"
                worksheet.write("C%s" % row, move_type, format4)
                worksheet.write("D%s" % row, each.partner_id.name if each.partner_id.name else "", format4)
                worksheet.write("E%s" % row, each.ref if each.ref else "", format4)
                worksheet.write("F%s" % row, each.partner_id.vat if each.partner_id.vat else "", format4)
                weight = 0
                quantity = 0
                total_qty = 0
                total_pack_size = 0
                for line in each.invoice_line_ids:
                    packet = []
                    if (
                        not line.product_uom_id.category_id
                        or line.product_uom_id.category_id == line.product_id.uom_id.category_id
                    ):
                        uom_factor = line.product_uom_id.factor if line.product_uom_id.factor != 0 else 1
                    else:
                        uom_factor = 1
                    if line.product_id.uom_id.uom_type != "reference" and line.product_id.uom_id.factor != 0:
                        product_uom_factor = line.product_id.uom_id.factor
                    else:
                        product_uom_factor = 1
                    line_weight = (line.product_id.weight * line.quantity) / uom_factor * product_uom_factor
                    weight += line_weight
                    quantity += line.quantity
                    if line.product_id.product_tmpl_id.pack_size_desc:
                        packet = [int(s) for s in line.product_id.product_tmpl_id.pack_size_desc.split() if s.isdigit()]
                        if packet:
                            total_qty += line.quantity * packet[0]
                            total_pack_size += packet[0]
                    else:
                        total_qty += 0
                worksheet.write("G%s" % row, "{:.2f}".format(weight), format_number)
                worksheet.write("H%s" % row, "{:.2f}".format(each.amount_total), format_number)
                worksheet.write("I%s" % row, "{:.2f}".format(quantity), format_number)
                worksheet.write("J%s" % row, "{:.2f}".format(total_pack_size), format_number)
                worksheet.write("K%s" % row, "{:.2f}".format(total_qty), format_number)
                row += 1
        else:
            # PRINT ALL THE INVOICES
            invoice_domain = []
            invoice_domain.append(("date", ">=", data["form"]["date_start"]))
            invoice_domain.append(("date", "<=", data["form"]["date_end"]))
            invoice_domain.append(("move_id.partner_id.country_id.code", "!=", "ES"))
            invoice_domain.append(("move_id.partner_id.country_id.code", "in", eu_country_codes))
            invoice_domain.append(("parent_state", "=", "posted"))
            invoice_domain.append(("tax_tag_ids", "in", account_tag_id.ids))
            invoice_domain.append(("move_id.move_type", "=", "out_invoice"))
            invoice_domain.append(("move_id.edi_state", "=", "sent"))
            invoices = self.env["account.move.line"].search(invoice_domain).mapped("move_id")

            for each in invoices:
                worksheet.write("A%s" % row, each.name if each.name else "", format4)
                worksheet.write(
                    "B%s" % row, each.partner_id.country_id.name if each.partner_id.country_id else "", format4
                )
                if each.move_type == "out_invoice":
                    move_type = "Dispatch"
                elif each.move_type == "in_invoice":
                    move_type = "Arrival"
                worksheet.write("C%s" % row, move_type, format4)
                worksheet.write("D%s" % row, each.partner_id.name if each.partner_id.name else "", format4)
                worksheet.write("E%s" % row, each.ref if each.ref else "", format4)
                worksheet.write("F%s" % row, each.partner_id.vat if each.partner_id.vat else "", format4)
                weight = 0
                quantity = 0
                total_qty = 0
                total_pack_size = 0
                for line in each.invoice_line_ids:
                    packet = []
                    if (
                        not line.product_uom_id.category_id
                        or line.product_uom_id.category_id == line.product_id.uom_id.category_id
                    ):
                        uom_factor = line.product_uom_id.factor if line.product_uom_id.factor != 0 else 1
                    else:
                        uom_factor = 1
                    if line.product_id.uom_id.uom_type != "reference" and line.product_id.uom_id.factor != 0:
                        product_uom_factor = line.product_id.uom_id.factor
                    else:
                        product_uom_factor = 1
                    line_weight = (line.product_id.weight * line.quantity) / uom_factor * product_uom_factor
                    weight += line_weight
                    quantity += line.quantity
                    if line.product_id.product_tmpl_id.pack_size_desc:
                        packet = [int(s) for s in line.product_id.product_tmpl_id.pack_size_desc.split() if s.isdigit()]
                        if packet:
                            total_qty += line.quantity * packet[0]
                            total_pack_size += packet[0]
                    else:
                        total_qty += 0
                worksheet.write("G%s" % row, "{:.2f}".format(weight), format_number)
                worksheet.write("H%s" % row, "{:.2f}".format(each.amount_total), format_number)
                worksheet.write("I%s" % row, "{:.2f}".format(quantity), format_number)
                worksheet.write("J%s" % row, "{:.2f}".format(total_pack_size), format_number)
                worksheet.write("K%s" % row, "{:.2f}".format(total_qty), format_number)
                row += 1

            # PRINT ALL THE BILLS
            bill_domain = []
            bill_domain.append(("date", ">=", data["form"]["date_start"]))
            bill_domain.append(("date", "<=", data["form"]["date_end"]))
            bill_domain.append(("move_id.partner_id.country_id.code", "!=", "ES"))
            bill_domain.append(("move_id.partner_id.country_id.code", "in", eu_country_codes))
            bill_domain.append(("parent_state", "=", "posted"))
            bill_domain.append(("tax_ids", "in", tax_ids.ids))
            bill_domain.append(("move_id.move_type", "=", "in_invoice"))
            invoices = self.env["account.move.line"].search(bill_domain).mapped("move_id")

            for each in invoices:
                worksheet.write("A%s" % row, each.name if each.name else "", format4)
                worksheet.write(
                    "B%s" % row, each.partner_id.country_id.name if each.partner_id.country_id else "", format4
                )
                if each.move_type == "out_invoice":
                    move_type = "Dispatch"
                elif each.move_type == "in_invoice":
                    move_type = "Arrival"
                worksheet.write("C%s" % row, move_type, format4)
                worksheet.write("D%s" % row, each.partner_id.name if each.partner_id.name else "", format4)
                worksheet.write("E%s" % row, each.ref if each.ref else "", format4)
                worksheet.write("F%s" % row, each.partner_id.vat if each.partner_id.vat else "", format4)
                weight = 0
                quantity = 0
                total_qty = 0
                total_pack_size = 0
                for line in each.invoice_line_ids:
                    packet = []
                    if (
                        not line.product_uom_id.category_id
                        or line.product_uom_id.category_id == line.product_id.uom_id.category_id
                    ):
                        uom_factor = line.product_uom_id.factor if line.product_uom_id.factor != 0 else 1
                    else:
                        uom_factor = 1
                    if line.product_id.uom_id.uom_type != "reference" and line.product_id.uom_id.factor != 0:
                        product_uom_factor = line.product_id.uom_id.factor
                    else:
                        product_uom_factor = 1
                    line_weight = (line.product_id.weight * line.quantity) / uom_factor * product_uom_factor
                    weight += line_weight
                    quantity += line.quantity
                    if line.product_id.product_tmpl_id.pack_size_desc:
                        packet = [int(s) for s in line.product_id.product_tmpl_id.pack_size_desc.split() if s.isdigit()]
                        if packet:
                            total_qty += line.quantity * packet[0]
                            total_pack_size += packet[0]
                    else:
                        total_qty += 0
                worksheet.write("G%s" % row, "{:.2f}".format(weight), format_number)
                worksheet.write("H%s" % row, "{:.2f}".format(each.amount_total), format_number)
                worksheet.write("I%s" % row, "{:.2f}".format(quantity), format_number)
                worksheet.write("J%s" % row, "{:.2f}".format(total_pack_size), format_number)
                worksheet.write("K%s" % row, "{:.2f}".format(total_qty), format_number)
                row += 1
