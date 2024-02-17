from odoo import models
from datetime import datetime

# from cStringIO import StringIO


class LogisticsReport(models.AbstractModel):
    _name = "report.bi_logistics_report.export_report_xlsx"
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
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = data["form"]["end_date"]
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        ws.merge_range("A1:D1", "Logistics Sales Report", boldl)
        ws.write("A3", "Logistics Company", boldl)
        ws.merge_range("B3:C3", logistics_id.name, center)
        ws.write("A4", "Company", boldl)
        ws.merge_range("B4:C4", self.env.company.name, center)
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
        ws.set_column("H:H", 20)
        ws.set_column("I:I", 20)
        ws.set_column("J:J", 20)
        ws.set_column("K:K", 20)

        row = 6

        ws.write("A%s" % row, "Order No", boldc)
        ws.write("B%s" % row, "Order Date", boldc)
        ws.write("C%s" % row, "Customer Name", boldc)
        ws.write("D%s" % row, "No of Lines", boldc)
        ws.write("E%s" % row, "Shipment Date", boldc)
        ws.write("F%s" % row, "Cost", boldc)
        ws.write("G%s" % row, "Additional Cost", boldc)
        ws.write("H%s" % row, "Logistics Cost", boldc)
        ws.write("I%s" % row, "Delivery Status", boldc)
        ws.write("J%s" % row, "Reason Code", boldc)
        ws.write("K%s" % row, "Resend Reason", boldc)

        warehouse_id = (
            self.env["logistics.master.line"]
            .search([("company_id", "=", self.env.company.id), ("logistic_id", "=", logistics_id.id)])
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
        pickings = self.env["stock.picking"].search(
            [
                ("state", "=", "done"),
                ("date_done", ">=", start_date),
                ("date_done", "<=", end_date),
                ("picking_type_code", "=", "outgoing"),
                ("location_id", "=", warehouse_id.lot_stock_id.id),
                ('is_reship','=', False)
            ]
        )
        row = 7
        total_cost = 0
        total_additional_cost = 0
        total_logistics_cost = 0
        for picking in pickings:

            # order = self.env["sale.order"].search([("picking_ids", "in", picking.ids)], limit=1)
            ws.write("A%s" % row, picking.origin, center)
            ws.write("B%s" % row, picking.sale_id.date_order.strftime("%d-%m-%Y") if picking.sale_id.date_order else "", center)
            ws.write("C%s" % row, picking.partner_id.name, center)
            no_of_lines = 0
            count = 1
            cost = 0
            additional_cost = 0
            logistics_id = self.env["logistics.master.line"].search(
                [
                    ("company_id", "=", self.env.company.id),
                    ("logistic_id", "=", logistics_id.id),
                    ("warehouse_id", "=", warehouse_id.id),
                ]
            )
            for line in picking.move_ids_without_package.filtered(lambda l: l.product_id.detailed_type == "product"):
                no_of_lines += 1
                if count <= logistics_id.per_line:
                    cost = logistics_id.cost
                else:
                    additional_cost += logistics_id.additional_cost
                count += 1

            ws.write("D%s" % row, no_of_lines, center)
            picking = picking
            required_picking = picking and picking[-1]
            ws.write("E%s" % row, required_picking.date_done.strftime("%d-%m-%Y") if required_picking else "", center)
            ws.write("F%s" % row, cost, center)
            total_cost += cost
            ws.write("G%s" % row, additional_cost, center)
            total_additional_cost += additional_cost
            logistics_costs = additional_cost+cost
            ws.write("H%s" % row, logistics_costs, center)
            total_logistics_cost += logistics_costs
            ws.write(
                "I%s" % row,
                picking.state,
                center,
            )
            if picking:
                ws.write(
                    "J%s" % row, picking[0].reason_code_id.display_name if picking[0].reason_code_id else "", center
                )
                ws.write("K%s" % row, picking[0].resend_reason if picking[0].resend_reason else "", center)
            row += 1

        ws.write("F%s" % row, total_cost, center)
        ws.write("G%s" % row, total_additional_cost, center)
        ws.write("H%s" % row, total_logistics_cost, center)


        pickings = self.env["stock.picking"].search(
            [
                ("state", "=", "done"),
                ("date_done", ">=", start_date),
                ("date_done", "<=", end_date),
                ("picking_type_code", "=", "outgoing"),
                ("location_id", "=", warehouse_id.lot_stock_id.id),
                ('is_reship','=', True)
            ]
        )

        row += 4
        ws.merge_range("A%s:D%s" %(row-1,row-1), "Reship Transfers", boldl)
        ws.write("A%s" % row, "Order No", boldc)
        ws.write("B%s" % row, "Order Date", boldc)
        ws.write("C%s" % row, "Customer Name", boldc)
        ws.write("D%s" % row, "No of Lines", boldc)
        ws.write("E%s" % row, "Shipment Date", boldc)
        ws.write("F%s" % row, "Cost", boldc)
        ws.write("G%s" % row, "Additional Cost", boldc)
        ws.write("H%s" % row, "Logistics Cost", boldc)
        ws.write("I%s" % row, "Delivery Status", boldc)
        ws.write("J%s" % row, "Reason Code", boldc)
        ws.write("K%s" % row, "Resend Reason", boldc)

        row += 1
        total_cost = 0
        total_additional_cost = 0
        total_logistics_cost = 0
        for picking in pickings:

            # order = self.env["sale.order"].search([("picking_ids", "in", picking.ids)], limit=1)
            ws.write("A%s" % row, picking.origin, center)
            ws.write("B%s" % row, picking.sale_id.date_order.strftime("%d-%m-%Y") if picking.sale_id.date_order else "", center)
            ws.write("C%s" % row, picking.partner_id.name, center)
            no_of_lines = 0
            count = 1
            cost = 0
            additional_cost = 0
            logistics_id = self.env["logistics.master.line"].search(
                [
                    ("company_id", "=", self.env.company.id),
                    ("logistic_id", "=", logistics_id.id),
                    ("warehouse_id", "=", warehouse_id.id),
                ]
            )
            for line in picking.move_ids_without_package.filtered(lambda l: l.product_id.detailed_type == "product"):
                no_of_lines += 1
                if count <= logistics_id.per_line:
                    cost = logistics_id.cost
                else:
                    additional_cost += logistics_id.additional_cost
                count += 1

            ws.write("D%s" % row, no_of_lines, center)
            picking = picking
            required_picking = picking and picking[-1]
            ws.write("E%s" % row, required_picking.date_done.strftime("%d-%m-%Y") if required_picking else "", center)
            ws.write("F%s" % row, -1*cost, center)
            total_cost += cost
            ws.write("G%s" % row, -1*additional_cost, center)
            total_additional_cost += additional_cost
            logistics_costs = additional_cost+cost
            ws.write("H%s" % row, -1*logistics_costs, center)
            total_logistics_cost += logistics_costs
            ws.write(
                "I%s" % row,
                picking.state,
                center,
            )
            if picking:
                ws.write(
                    "J%s" % row, picking[0].reason_code_id.display_name if picking[0].reason_code_id else "", center
                )
                ws.write("K%s" % row, picking[0].resend_reason if picking[0].resend_reason else "", center)
            row += 1

        ws.write("F%s" % row, -1*total_cost, center)
        ws.write("G%s" % row, -1*total_additional_cost, center)
        ws.write("H%s" % row, -1*total_logistics_cost, center)

        # fp = StringIO()
        # workbook.save(fp)
        # fp.seek(0)
        # datas = base64.encodestring(fp.read())
        # file_name = "demo.xlsx"
        # attachment_data = {
        # 'name':file_name,
        # 'datas_fname':file_name,
        # 'datas':datas,
        # 'res_model':"logistics.wizard",
        # }
        # self.env['ir.attachment'].create(attachment_data)
