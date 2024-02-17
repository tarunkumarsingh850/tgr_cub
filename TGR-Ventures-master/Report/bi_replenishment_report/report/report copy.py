from odoo import models
import json


class ReplenishmentReportXlsx(models.AbstractModel):
    _name = "report.bi_replenishment_report.report_replenishment_xlsx"
    _description = "Replenishment XLSX Report"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Replenishment Report")
        format1_header = workbook.add_format({"bold": True, "align": "center", "valign": "vcenter", "border": 1})
        format2_header = workbook.add_format({"align": "center", "valign": "vcenter", "border": 1})
        format4_title = workbook.add_format({"bold": True, "align": "center", "font_size": 24, "border": 1})
        worksheet.set_row(0, 30)
        worksheet.set_row(7, 30)

        worksheet.set_column("A:A", 10)
        worksheet.set_column("B:B", 10)
        worksheet.set_column("C:C", 10)
        worksheet.set_column("D:D", 10)
        worksheet.set_column("E:E", 10)
        worksheet.set_column("F:F", 10)
        worksheet.set_column("G:G", 10)
        worksheet.set_column("H:H", 10)
        worksheet.set_column("I:I", 10)
        worksheet.set_column("J:J", 10)
        worksheet.set_column("K:K", 10)
        worksheet.set_column("L:L", 10)
        worksheet.set_column("M:M", 10)
        worksheet.set_column("N:N", 10)
        worksheet.set_column("O:O", 10)
        worksheet.set_column("P:P", 10)
        worksheet.set_column("Q:Q", 10)
        worksheet.set_column("R:R", 10)
        worksheet.set_column("S:S", 10)
        worksheet.set_column("T:T", 20)
        worksheet.set_column("U:U", 15)
        worksheet.set_column("V:V", 15)
        worksheet.set_column("W:W", 15)
        worksheet.set_column("X:X", 15)
        worksheet.set_column("Y:Y", 15)
        worksheet.set_column("Z:Z", 15)
        worksheet.set_column("AA:AA", 15)
        worksheet.set_column("AB:AB", 15)
        worksheet.set_column("AC:AC", 15)

        worksheet.merge_range("A1:W1", "Replenishment Report", format4_title)
        worksheet.merge_range("A2:W2", "")

        worksheet.write("A4", "1", format1_header)
        worksheet.write("B4", "2", format1_header)
        worksheet.write("C4", "3", format1_header)
        worksheet.write("D4", "4", format1_header)
        worksheet.write("E4", "5", format1_header)
        worksheet.write("F4", "6", format1_header)
        worksheet.write("G4", "7", format1_header)
        worksheet.write("H4", "8", format1_header)
        worksheet.write("I4", "9", format1_header)
        worksheet.write("J4", "10", format1_header)
        worksheet.write("K4", "11", format1_header)
        worksheet.write("L4", "12", format1_header)

        worksheet.write("M4", "Av.", format1_header)
        worksheet.write("N4", "Phys.", format1_header)
        worksheet.write("O4", "Alloc.", format1_header)
        worksheet.write("P4", "On.ord.", format1_header)
        worksheet.write("Q4", "Ideal", format1_header)
        worksheet.write("R4", "Avail", format1_header)
        worksheet.write("S4", "Order Qty.", format1_header)
        worksheet.write("T4", "", format1_header)
        worksheet.write("U4", "Tax Category", format1_header)
        worksheet.write("V4", "Warehouse", format1_header)
        worksheet.write("W4", "Inventory ID", format1_header)
        worksheet.write("X4", "Sale Quantity", format1_header)
        worksheet.write("Y4", "Lead Days Date", format1_header)
        worksheet.write("Z4", "Qty Forecast", format1_header)
        worksheet.write("AA4", "Qty to Order", format1_header)
        worksheet.write("AB4", "Product Min Qty", format1_header)
        worksheet.write("AC4", "Product Max Qty", format1_header)
        row = 5

        all_product_ids = self.env["product.product"].search([])
        product_ids = (
            self.env["stock.replenishment.info"]
            .search([("product_id", "in", all_product_ids.ids)])
            .mapped("product_id")
        )
        for product in product_ids:
            replenishment_ids = self.env["stock.replenishment.info"].search([("product_id", "=", product.id)])
            brand = data["form"]["brand_breeder_id"]
            replenishment_ids = (
                replenishment_ids.product_id.filtered(lambda x: x.product_breeder_id == brand)
                if brand
                else replenishment_ids
            )
            inventory = data["form"]["inventory_id"]
            replenishment_ids = (
                replenishment_ids.product_id.filtered(lambda x: x.property_stock_inventory == inventory)
                if inventory
                else replenishment_ids
            )
            flower_type = data["form"]["flower_type_id"]
            replenishment_ids = (
                replenishment_ids.product_id.filtered(lambda x: x.flower_type_id == flower_type)
                if flower_type
                else replenishment_ids
            )
            size = data["form"]["size_id"]
            replenishment_ids = (
                replenishment_ids.product_id.filtered(lambda x: x.product_size_id == size)
                if size
                else replenishment_ids
            )
            month_list = []
            for orders in replenishment_ids:
                lead_days_date = json.loads(orders.json_lead_days)["lead_days_date"]
                qty_forecast = json.loads(orders.json_lead_days)["qty_forecast"]
                qty_to_order = json.loads(orders.json_lead_days)["qty_to_order"]
                product_min_qty = json.loads(orders.json_lead_days)["product_min_qty"]
                product_max_qty = json.loads(orders.json_lead_days)["product_max_qty"]
                result = json.loads(orders.json_replenishment_history)["replenishment_history"]
                for month in result:
                    quantity_sale = 0
                    if not month["name"] in month_list:
                        quantity_sale += month["quantity"]
                        month_list.append(month["name"])
                        worksheet.write("T%s" % row, orders.product_id.name, format2_header)
                        worksheet.write("X%s" % row, quantity_sale, format2_header)
                        worksheet.write("Y%s" % row, lead_days_date, format2_header)
                        worksheet.write("Z%s" % row, qty_forecast, format2_header)
                        worksheet.write("AA%s" % row, qty_to_order, format2_header)
                        worksheet.write("AB%s" % row, product_min_qty, format2_header)
                        worksheet.write("AC%s" % row, product_max_qty, format2_header)
                        row += 1
