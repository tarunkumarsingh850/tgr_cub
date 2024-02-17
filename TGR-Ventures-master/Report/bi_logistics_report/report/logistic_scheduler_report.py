from odoo import models

# from cStringIO import StringIO


class LogisticsSchedulerReport(models.AbstractModel):
    _name = "report.bi_logistics_report.export_scheduler_report_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        ws = workbook.add_worksheet("Logistics Report")
        boldl = workbook.add_format({"bold": True, "align": "left"})
        boldc = workbook.add_format({"bold": True, "align": "center"})
        center = workbook.add_format({"align": "center"})

        # WIZARD VALUES
        if data["form"]["logistics_id"]:
            logistics_id = self.env["bi.logistics.master"].search([("id", "=", data["form"]["logistics_id"])])

        start_date = data["form"]["start_date"]
        end_date = data["form"]["end_date"]

        ws.merge_range("A1:D1", "Logistics Sales Report", boldl)
        ws.write("A3", "Logistics Company", boldl)
        ws.merge_range("B3:C3", logistics_id.name, center)
        ws.write("A4", "Company", boldl)
        ws.merge_range("B4:C4", self.env.user.company_id.name, center)
        ws.write("F3", "Start Date", boldl)
        ws.write("F4", "End Date", boldl)

        ws.write("G3", start_date.strftime("%d-%m-%Y"), center)
        ws.write("G4", end_date.strftime("%d-%m-%Y"), center)

        ws.set_column("A:A", 20)
        ws.set_column("B:B", 20)
        ws.set_column("C:C", 20)
        ws.set_column("D:D", 20)
        ws.set_column("E:E", 20)
        ws.set_column("F:F", 20)
        ws.set_column("G:G", 20)

        row = 6

        ws.write("A%s" % row, "Order No", boldc)
        ws.write("B%s" % row, "Order Date", boldc)
        ws.write("C%s" % row, "Customer Name", boldc)
        ws.write("D%s" % row, "No of Lines", boldc)
        ws.write("E%s" % row, "Cost", boldc)
        ws.write("F%s" % row, "Additional Cost", boldc)
        ws.write("G%s" % row, "Logistics Cost", boldc)

        warehouse_id = (
            self.env["logistics.master.line"]
            .search([("company_id", "=", self.env.user.company_id.id), ("logistic_id", "=", logistics_id.id)])
            .mapped("warehouse_id")
        )
        sale_order_ids = self.env["sale.order"].search(
            [
                ("date_order", ">=", start_date),
                ("date_order", "<=", end_date),
                ("warehouse_id", "=", warehouse_id.id),
                ("state", "=", "sale"),
            ]
        )

        row = 7
        for order in sale_order_ids:
            ws.write("A%s" % row, order.name, center)
            ws.write("B%s" % row, order.date_order.strftime("%d-%m-%Y"), center)
            ws.write("C%s" % row, order.partner_id.name, center)
            no_of_lines = 0
            count = 1
            cost = 0
            additional_cost = 0
            logistics_id = self.env["logistics.master.line"].search(
                [
                    ("company_id", "=", self.env.user.company_id.id),
                    ("logistic_id", "=", logistics_id.id),
                    ("warehouse_id", "=", warehouse_id.id),
                ]
            )
            for line in order.order_line.filtered(lambda l: l.product_id.detailed_type == "product"):
                no_of_lines += 1
                if count <= logistics_id.per_line:
                    cost = logistics_id.cost
                else:
                    additional_cost += logistics_id.additional_cost
                count += 1

            ws.write("D%s" % row, no_of_lines, center)
            ws.write("E%s" % row, cost, center)
            ws.write("F%s" % row, additional_cost, center)
            ws.write("G%s" % row, order.logistics_costs, center)
            row += 1
