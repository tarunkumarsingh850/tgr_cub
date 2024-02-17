from odoo import models


class PickingReport(models.AbstractModel):
    _name = "report.bi_picking_excel_report.picking_report_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Picking Report"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Picking Report")
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

        worksheet.write("A1", "NAME", format_wrap_text)
        worksheet.write("B1", "ADDRESS", format_wrap_text)
        worksheet.write("C1", "CITY", format_wrap_text)
        worksheet.write("D1", "LOCATION", format_wrap_text)
        worksheet.write("E1", "POSTAL CODE", format_wrap_text)
        worksheet.write("F1", "COUNTRY", format_wrap_text)
        worksheet.write("G1", "COUNTRY CODE", format_wrap_text)
        worksheet.write("H1", "Recipient contact phone", format_wrap_text)
        worksheet.write("I1", "E-mail ", format_wrap_text)
        worksheet.write("J1", "Customer reference", format_wrap_text)
        domain = []
        warehouse = data["form"]["warehouse_id"]
        batch_id = data["form"]["batch_id"]
        if warehouse:
            domain.append(("location_id.warehouse_id", "=", warehouse))
        data["form"]["date_end"]
        # if date_end:
        #     domain.append(("scheduled_date", "<=", date_end))
        # date_start = data["form"]["date_start"]
        # if date_start:
        #     domain.append(("scheduled_date", ">=", date_start))
        if batch_id:
            domain.append(("batch_id", "=", batch_id))
        picking_ids = self.env["stock.picking"].search(domain)
        row = 2
        for each in picking_ids:
            street = each.partner_id.street
            if each.partner_id.street2:
                street = each.partner_id.street + "," + each.partner_id.street2
            worksheet.write("A%s" % row, each.partner_id.name if each.partner_id else "", format4)
            worksheet.write("B%s" % row, street, format4)
            worksheet.write("C%s" % row, each.partner_id.city, format4)
            worksheet.write(
                "D%s" % row, each.partner_id.state_id.name if each.partner_id.state_id.name else "", format4
            )
            worksheet.write("E%s" % row, each.partner_id.zip if each.partner_id.zip else "", format4)
            worksheet.write("F%s" % row, each.country_id.name if each.country_id.name else "", format4)
            worksheet.write("G%s" % row, each.country_id.code if each.country_id.code else "", format4)
            worksheet.write("H%s" % row, each.partner_id.phone if each.partner_id.phone else "", format4)
            worksheet.write("I%s" % row, each.partner_id.email if each.partner_id.email else "", format4)
            worksheet.write("J%s" % row, each.origin if each.origin else "", format4)
            row += 1
