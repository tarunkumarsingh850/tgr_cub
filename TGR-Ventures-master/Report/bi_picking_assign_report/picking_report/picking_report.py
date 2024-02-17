# See LICENSE file for full copyright and licensing details.
from odoo import models
from datetime import datetime


class ReportSale(models.AbstractModel):
    _name = "report.bi_picking_assign_report.assign_order_report_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        date_start = data["form"]["date_start"]
        date_end = data["form"]["date_end"]
        picker_ids = data["form"]["picker_ids"]
        warehouse_ids = data["form"]["warehouse_ids"]

        worksheet = workbook.add_worksheet("Report")
        format1 = workbook.add_format(
            {"font_size": 14, "bottom": True, "right": True, "left": True, "top": True, "align": "center", "bold": True}
        )
        format3 = workbook.add_format({"bottom": True, "top": True, "font_size": 12})
        font_size_8 = workbook.add_format({"bottom": True, "top": True, "right": True, "left": True, "font_size": 8})
        justify = workbook.add_format({"bottom": True, "top": True, "right": True, "left": True, "font_size": 12})
        format3.set_align("center")
        font_size_8.set_align("center")
        justify.set_align("justify")
        format1.set_align("center")
        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 20)
        worksheet.set_column("D:D", 20)
        worksheet.set_column("E:E", 20)
        worksheet.set_column("F:F", 20)
        worksheet.set_column("G:G", 20)
        worksheet.set_column("H:H", 20)
        worksheet.set_column("I:I", 20)
        worksheet.set_column("J:J", 20)
        worksheet.set_column("K:K", 10)
        worksheet.set_column("L:L", 10)
        worksheet.set_column("M:M", 10)
        worksheet.set_column("N:N", 10)
        worksheet.set_column("O:O", 10)

        boldc = workbook.add_format({"bold": True, "align": "center"})
        boldl = workbook.add_format({"bold": True, "align": "left"})

        left = workbook.add_format({"align": "left"})
        heading_format = workbook.add_format({"bold": True, "align": "center", "font_color": "black"})

        worksheet.merge_range("A1:E1", "Report", boldc)
        filter_row = 2

        worksheet.write("A%s" % filter_row, "Date From", boldl)
        worksheet.write("B%s" % filter_row, datetime.strptime(date_start, "%Y-%m-%d").strftime("%d-%m-%Y"), left)
        worksheet.write("C%s" % filter_row, "Date To", boldl)
        worksheet.write("D%s" % filter_row, datetime.strptime(date_end, "%Y-%m-%d").strftime("%d-%m-%Y"), left)

        row = 4

        domain = [("state", "in", ["draft", "waiting", "confirmed", "assigned", "done"])]
        if date_start:
            domain.append(("scheduled_date", ">=", date_start))
        if date_end:
            domain.append(("scheduled_date", "<=", date_end))
        if picker_ids:
            domain.append(("user_id", "in", picker_ids))
        if warehouse_ids:
            domain.append(("picking_type_id.warehouse_id", "in", warehouse_ids))

        picking_ids = self.env["stock.picking"].search(domain)
        warehouse_ids = self.env["stock.picking"].search(domain).picking_type_id.sudo().mapped("warehouse_id")
        for each in warehouse_ids:
            worksheet.write("A%s" % row, "Warehouse", heading_format)
            worksheet.write("B%s" % row, each.sudo().name, heading_format)
            row += 1
            worksheet.write("A%s" % row, "Transfer", heading_format)
            worksheet.write("B%s" % row, "Partner", heading_format)
            worksheet.write("C%s" % row, "Date", heading_format)
            worksheet.write("D%s" % row, "Picker", heading_format)
            worksheet.write("E%s" % row, "Carrier", heading_format)
            row += 1
            for each_pick in picking_ids:
                if each.id == each_pick.picking_type_id.warehouse_id.id:
                    worksheet.write("A%s" % row, each_pick.name, left)
                    worksheet.write("B%s" % row, each_pick.partner_id.name if each_pick.partner_id else "", left)
                    worksheet.write("C%s" % row, each_pick.scheduled_date.strftime("%d-%m-%Y"), left)
                    worksheet.write("D%s" % row, each_pick.user_id.name, left)
                    worksheet.write("E%s" % row, each_pick.carrier_id.name if each_pick.carrier_id else "", left)
                    row += 1
