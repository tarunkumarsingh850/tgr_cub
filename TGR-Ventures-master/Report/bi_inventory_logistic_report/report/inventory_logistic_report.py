from odoo import models
from datetime import datetime


class InventoryLogisticReport(models.AbstractModel):
    _name = "report.bi_inventory_logistic_report.inventory_report_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, record):
        ws = workbook.add_worksheet("Inventory Logistic Report")
        format1 = workbook.add_format({"bold": 1, "align": "center", "font_size": 11, "valign": "vcenter"})
        format2 = workbook.add_format({"align": "center", "font_size": 10, "valign": "vcenter"})
        format3 = workbook.add_format({"bold": 1, "align": "left", "font_size": 10, "valign": "vcenter"})
        format4 = workbook.add_format({"align": "left", "font_size": 10, "valign": "vcenter"})
        start_date = data["start_date"]
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = data["end_date"]
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        company = self.env.company
        pickings = self.env["stock.picking"].search(
            [
                ("state", "=", "done"),
                ("date_done", ">=", start_date),
                ("date_done", "<=", end_date),
                ("picking_type_code", "=", "outgoing"),
                ("company_id", "=", company.id),
            ]
        )
        wholesale_pickings = pickings.filtered(
            lambda l: l.partner_id and l.partner_id.customer_class_id and l.partner_id.customer_class_id.is_wholesales
        )
        ws.set_column("A:A", 30)
        ws.set_column("B:B", 30)
        ws.set_column("C:C", 30)
        ws.set_column("D:D", 30)
        ws.merge_range("A1:D2", "Inventory Logistic Report", format1)
        ws.write("A3", "Logistics Company", format3)
        ws.write("B3", "WHOLESALE POINT", format4)
        ws.write("A4", "Company", format3)
        ws.write("B4", company.name, format4)
        ws.write("C3", "Start Date", format3)
        ws.write("C4", "End Date", format3)
        ws.write("D3", start_date.strftime("%d-%m-%Y"), format4)
        ws.write("D4", end_date.strftime("%d-%m-%Y"), format4)
        row = 6
        ws.write("A%s" % row, "Sale Order No", format1)
        ws.write("B%s" % row, "Transfer No", format1)
        ws.write("C%s" % row, "Shipping cost", format1)
        ws.write("D%s" % row, "Reason code", format1)
        row = 7
        for picking in wholesale_pickings:
            if picking.sale_id:
                cost = 0
                for move in picking.move_ids_without_package:
                    cost += move.cost
                ws.write("A%s" % row, picking.sale_id.name, format2)
                ws.write("B%s" % row, picking.name, format2)
                ws.write("C%s" % row, cost, format2)
                ws.write("D%s" % row, picking.reason_code_id.display_name if picking.reason_code_id else "", format2)
                row += 1
