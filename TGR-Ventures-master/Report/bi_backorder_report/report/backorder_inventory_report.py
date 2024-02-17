from odoo import models, _
from datetime import datetime


class BackorderInventoryReport(models.AbstractModel):
    _name = "report.bi_backorder_report.backorder_report_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, record):
        ws = workbook.add_worksheet("Backorder Inventory Report")
        format1 = workbook.add_format({"bold": 1, "align": "center", "font_size": 11, "valign": "vcenter"})
        format2 = workbook.add_format({"align": "center", "font_size": 10, "valign": "vcenter"})
        format3 = workbook.add_format({"bold": 1, "align": "left", "font_size": 10, "valign": "vcenter"})
        format4 = workbook.add_format({"align": "left", "font_size": 10, "valign": "vcenter"})
        start_date = data["start_date"]
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = data["end_date"]
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        not_available = _("Not Available")
        location_id = self.env["stock.location"].search([("id", "=", 190), ("company_id", "=", 11)])
        company_id = self.env["res.company"].search([("id", "=", 11)])
        # generate report only for TGR Ventures Corp USA company
        if location_id and company_id:
            ws.set_column("A:A", 30)
            ws.set_column("B:B", 30)
            ws.set_column("C:C", 30)
            ws.set_column("D:D", 30)
            ws.set_column("E:E", 30)
            ws.set_column("F:F", 30)
            ws.set_column("G:G", 30)
            ws.set_column("H:H", 30)
            ws.merge_range("A1:F2", "Backorder Inventory Report", format1)
            ws.merge_range("A3:F3", company_id.name, format1)
            ws.write("A4", "Start Date", format3)
            ws.write("E4", "End Date", format3)
            ws.write("B4", start_date.strftime("%d-%m-%Y"), format4)
            ws.write("F4", end_date.strftime("%d-%m-%Y"), format4)
            row = 6
            ws.write("A%s" % row, "Date", format1)
            ws.write("B%s" % row, "Customer Name", format1)
            ws.write("C%s" % row, "Address", format1)
            ws.write("D%s" % row, "Transfer no", format1)
            ws.write("E%s" % row, "Sale Order no", format1)
            ws.write("F%s" % row, "Product", format1)
            ws.write("G%s" % row, "SKU", format1)
            ws.write("H%s" % row, "Payment Status", format1)
            pickings = self.env["stock.picking"].search(
                [
                    ("products_availability", "=", not_available),
                    ("scheduled_date", ">=", start_date),
                    ("scheduled_date", "<=", end_date),
                    ("picking_type_code", "=", "outgoing"),
                    ("company_id", "=", company_id.id),
                    ("location_id", "=", location_id.id),
                ]
            )
            row += 1
            for picking in pickings:
                stock_moves = picking.move_ids_without_package.filtered(lambda l: l.forecast_availability < 0)
                payment_status = ""
                if picking.payment_status and picking.payment_status == "not_paid":
                    payment_status = "Not Paid"
                elif picking.payment_status and picking.payment_status == "paid":
                    payment_status = "Paid"
                elif picking.payment_status and picking.payment_status == "credit":
                    payment_status = "Credit Customer"
                elif picking.payment_status and picking.payment_status == "paid_and_batched":
                    payment_status = "Processing/Batched"
                for move in stock_moves:
                    address = ""
                    if picking.partner_id.street:
                        address += picking.partner_id.street
                    if picking.partner_id.street2:
                        address += ", " + picking.partner_id.street2
                    if picking.partner_id.city:
                        address += ", " + picking.partner_id.city
                    if picking.partner_id.country_id:
                        address += ", " + picking.partner_id.country_id.name
                    ws.write("A%s" % row, picking.create_date.strftime("%Y-%m-%d"), format2)
                    ws.write("B%s" % row, picking.partner_id.name, format2)
                    ws.write("C%s" % row, address, format2)
                    ws.write("D%s" % row, picking.name, format2)
                    ws.write("E%s" % row, picking.origin if picking.origin else "", format2)
                    ws.write("F%s" % row, move.product_id.name, format2)
                    ws.write("G%s" % row, move.product_sku if move.product_sku else "", format2)
                    ws.write("H%s" % row, payment_status, format2)
                    row += 1
