from odoo import models


class RowPickingReport(models.AbstractModel):
    _name = "report.bi_row_picking_report.row_picking_report_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "RoW Picking Report"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("RoW Picking Report")
        worksheet.set_column("A:A", 10)
        worksheet.set_column("B:B", 25)
        worksheet.set_column("C:C", 30)
        worksheet.set_column("D:D", 40)
        worksheet.set_column("E:E", 10)
        worksheet.set_column("F:F", 30)
        worksheet.set_column("G:G", 30)
        worksheet.set_column("H:H", 15)
        worksheet.set_column("I:I", 10)
        worksheet.set_column("J:J", 20)
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

        worksheet.write("A1", "Client", format_wrap_text)
        worksheet.write("B1", "Order", format_wrap_text)
        worksheet.write("C1", "SKU", format_wrap_text)
        worksheet.write("D1", "Description", format_wrap_text)
        worksheet.write("E1", "Quantity", format_wrap_text)
        worksheet.write("F1", "Address Line 1", format_wrap_text)
        worksheet.write("G1", "Address Line 2", format_wrap_text)
        worksheet.write("H1", "Country", format_wrap_text)
        worksheet.write("I1", "Post Code", format_wrap_text)
        worksheet.write("J1", "Service", format_wrap_text)
        # warehouse = data["form"]["warehouse_id"]
        lines.location_id
        batch_id = data["form"]["batch_id"]
        domain = []
        # domain = [("location_id", "=", location.id),('country_id.country_group_id.id', 'not in', ['1','3'])]
        # date_end = data["form"]["date_end"]
        # if date_end:
        #     domain.append(("scheduled_date", "<=", date_end))
        # date_start = data["form"]["date_start"]
        # if date_start:
        #     domain.append(("scheduled_date", ">=", date_start))
        if batch_id:
            domain.append(("batch_id", "=", batch_id))
        picking_ids = self.env["stock.picking"].search(domain)
        row = 2
        for each in picking_ids.move_ids_without_package:
            worksheet.write("A%s" % row, "TGR", format4)
            worksheet.write("B%s" % row, each.picking_id.origin, format4)
            worksheet.write("C%s" % row, each.product_id.default_code, format4)
            worksheet.write("D%s" % row, each.product_id.name, format4)
            worksheet.write("E%s" % row, each.product_uom_qty if each.product_uom_qty else "", format4)
            worksheet.write(
                "F%s" % row, each.picking_id.partner_id.street if each.picking_id.partner_id.street else "", format4
            )
            worksheet.write(
                "G%s" % row, each.picking_id.partner_id.street2 if each.picking_id.partner_id.street2 else "", format4
            )
            worksheet.write(
                "H%s" % row,
                each.picking_id.partner_id.country_id.name if each.picking_id.partner_id.country_id else "",
                format4,
            )
            worksheet.write(
                "I%s" % row, each.picking_id.partner_id.zip if each.picking_id.partner_id.zip else "", format4
            )
            worksheet.write("J%s" % row, each.picking_id.carrier_id.name if each.picking_id.carrier_id else "", format4)
            row += 1
