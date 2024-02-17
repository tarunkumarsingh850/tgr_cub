from odoo import models
from datetime import date


class ReportExcel(models.AbstractModel):
    _name = "report.bi_consignment_report.consign_report_id"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet("Consignment Report")
        po_ids = data["form"]["po_ids"]
        start_date = data["form"]["start_date"]
        end_date = data["form"]["end_date"]
        cost_percentage = data["form"]["cost_percentage"]

        table_head_format = workbook.add_format(
            {"align": "center", "border": 1, "valign": "vcenter", "bg_color": "#D6D6D6"}
        )

        table_data_format = workbook.add_format(
            {
                "font_size": 10,
                "align": "center",
                "valign": "vcenter",
                "border": 1,
            }
        )

        total_format = workbook.add_format({"bold": True, "align": "center"})

        date_today = date.today().strftime("%d-%m-%Y")
        sheet.write("A1", "Consignment Orders Report           Date: %s" % date_today)
        sheet.write("A2", "PO \nNo", table_head_format)
        sheet.write("B2", "SKU", table_head_format)
        sheet.write("C2", "Description", table_head_format)
        sheet.write("D2", "Total Stock \npurchased", table_head_format)
        sheet.write("E2", "Remaining \nStock Qty", table_head_format)
        sheet.write("F2", "Total Qty \nSold", table_head_format)
        sheet.write("G2", "Sold Qty \n(Period)", table_head_format)
        sheet.write("H2", "Unit cost", table_head_format)
        sheet.write("I2", "Total to Pay \n(Period)", table_head_format)
        sheet.write("J2", "Total Paid", table_head_format)

        sheet.set_row(1, 30)
        sheet.merge_range("A1:E1", None)
        sheet.set_column("A:A", 10)
        sheet.set_column("B:B", 30)
        sheet.set_column("C:C", 30)
        sheet.set_column("D:D", 10)
        sheet.set_column("E:E", 10)
        sheet.set_column("F:F", 10)
        sheet.set_column("G:G", 10)
        sheet.set_column("H:H", 15)
        sheet.set_column("I:I", 15)

        if po_ids:
            rec_list = self.env["purchase.order"].search([("id", "in", po_ids)], order="date_order ASC")
        else:
            rec_list = self.env["purchase.order"].search(
                [("date_order", ">=", start_date), ("date_order", "<=", end_date), ("is_consignment_order", "=", True)],
                order="date_order ASC",
            )

        sum_total_to_pay = 0
        row = 3
        for rec in rec_list:
            sheet.write("A%s" % row, rec.name, table_data_format)
            if rec.order_line:
                for rec_line in rec.order_line:
                    total_sold_in_period = 0
                    total_qty_purchased = 0
                    total_qty_sold = 0
                    total_paid = 0
                    total_to_pay = 0
                    sheet.write("B%s" % row, rec_line.product_id.default_code, table_data_format)
                    sheet.write("C%s" % row, rec_line.product_id.name, table_data_format)

                    po_order_ids = (
                        self.env["purchase.order"]
                        .search([("is_consignment_order", "=", True)])
                        .filtered(
                            lambda po: any(ord_line.product_id == rec_line.product_id for ord_line in po.order_line)
                        )
                    )

                    for po_line in po_order_ids.order_line.filtered(
                        lambda ord_line: ord_line.product_id == rec_line.product_id
                    ):
                        total_qty_purchased += po_line.qty_received
                        total_qty_sold += po_line.quantity_sold
                        total_paid += po_line.quantity_sold * po_line.price_unit

                    sheet.write("D%s" % row, total_qty_purchased, table_data_format)
                    sheet.write("E%s" % row, rec_line.qty_received - rec_line.quantity_sold, table_data_format)
                    sheet.write("F%s" % row, total_qty_sold, table_data_format)

                    sale_order_lines = (
                        self.env["so.line"]
                        .search(
                            [
                                # ('po_id','=', rec.id),
                                ("create_date", ">=", start_date),
                                ("create_date", "<=", end_date),
                            ]
                        )
                        .filtered(lambda so: so.so_line_id.product_id == rec_line.product_id)
                    )

                    for sold_so in sale_order_lines:
                        total_sold_in_period += sold_so.so_sold_qty
                        # sheet.write('F%s'%row, sold_so.so_line_id.order_id.name, table_data_format)
                        # sheet.write('G%s'%row, sold_so.so_sold_qty, table_data_format)
                        # row+=1

                    paid_po_ids = (
                        self.env["purchase.order"]
                        .search(
                            [
                                ("is_consignment_order", "=", True),
                                ("date_order", ">=", start_date),
                                ("date_order", "<=", end_date),
                            ]
                        )
                        .filtered(
                            lambda po: any(ord_line.product_id == rec_line.product_id for ord_line in po.order_line)
                        )
                    )

                    for line in paid_po_ids.order_line.filtered(
                        lambda ord_line: ord_line.product_id == rec_line.product_id
                    ):
                        total_to_pay += (line.qty_received - line.quantity_sold) * line.price_unit
                    sum_total_to_pay += total_to_pay

                    if cost_percentage:
                        cost = rec_line.product_id.standard_price * cost_percentage / 100
                        unit_cost = (rec_line.product_id.standard_price - cost) * rec_line.product_uom_qty
                    else:
                        unit_cost = rec_line.product_id.standard_price * rec_line.product_uom_qty

                    sheet.write("G%s" % row, total_sold_in_period, table_data_format)
                    sheet.write("H%s" % row, round(unit_cost, 2), table_data_format)
                    sheet.write("I%s" % row, total_to_pay, table_data_format)
                    sheet.write("J%s" % row, total_paid, table_data_format)
                    row += 1
            else:
                row += 1
        sheet.write("I%s" % row, sum_total_to_pay, total_format)
