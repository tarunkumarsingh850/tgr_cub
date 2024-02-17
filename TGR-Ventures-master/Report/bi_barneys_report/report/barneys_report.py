from odoo import models
from datetime import datetime


class BarneysReport(models.AbstractModel):
    _name = "report.bi_barneys_report.generate_barneys_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        ws = workbook.add_worksheet("Barney's Summary Report")
        boldl = workbook.add_format({"bold": True, "align": "left"})
        boldc = workbook.add_format({"bold": True, "align": "center", "bg_color": "#808080"})
        total_format = workbook.add_format({"bold": True, "align": "center"})
        center = workbook.add_format({"align": "center"})
        right = workbook.add_format({"align": "right"})

        # WIZARD VALUES
        start_date = data["form"]["start_date"]
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = data["form"]["end_date"]
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        ws.merge_range("A1:D1", "Barney's Report", boldl)
        ws.write("A3", "Start Date", boldl)
        ws.write("A4", "End Date", boldl)
        ws.write("B3", start_date.strftime("%d-%m-%Y"), center)
        ws.write("B4", end_date.strftime("%d-%m-%Y"), center)

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
        ws.set_column("L:L", 20)
        ws.set_column("M:M", 20)
        ws.set_column("N:N", 20)
        ws.set_column("O:O", 20)
        ws.set_column("P:P", 20)
        ws.set_column("Q:Q", 20)
        ws.set_column("R:R", 20)

        row = 6

        ws.write("A%s" % row, "Order No", boldc)
        ws.write("B%s" % row, "Order Date", boldc)
        ws.write("C%s" % row, "No. of Products", boldc)
        ws.write("D%s" % row, "Total Sales Amount", boldc)
        ws.write("E%s" % row, "COGS", boldc)
        ws.write("F%s" % row, "COGS(in USD)", boldc)
        ws.write("G%s" % row, "Free Products", boldc)
        ws.write("H%s" % row, "Free Products (in USD)", boldc)
        ws.write("I%s" % row, "New Sales Tax", boldc)
        ws.write("J%s" % row, "Shipping Charge", boldc)
        ws.write("K%s" % row, "STAMPS Charge", boldc)
        ws.write("L%s" % row, "Payment Surcharge", boldc)
        ws.write("M%s" % row, "Picking/Packing Cost", boldc)
        ws.write("N%s" % row, "Gross Margin", boldc)
        ws.write("O%s" % row, "Gross Margin Amount", boldc)
        ws.write("P%s" % row, "TGR Profit", boldc)
        ws.write("Q%s" % row, "Barneys Profit", boldc)

        sale_order_ids = self.env["sale.order"].search(
            [
                ("date_order", ">=", start_date),
                ("date_order", "<=", end_date),
                ("state", "=", "sale"),
                ("is_barneys_dropshipping", "=", True),
            ]
        )

        row = 7
        sum_sale_amount = 0
        sum_cogs = 0
        sum_cogs_usd = 0
        sum_tax = 0
        sum_payment_surcharge = 0
        sum_picking_cost = 0
        sum_profit = 0
        sum_tgr_profit = 0
        sum_barneys_profit = 0
        sum_stamps = 0
        sum_shipping_charge = 0
        sum_deduct_cogs = 0
        sum_deduct_cogs_usd = 0
        total_amount_to_be_collected = 0
        amount_to_be_collected = 0
        for sale in sale_order_ids:
            sku_count = len(sale.order_line.filtered(lambda pline: pline.product_id.detailed_type == "product"))
            ws.write("A%s" % row, sale.name, center)
            ws.write("B%s" % row, sale.date_order.strftime("%d-%m-%Y"), center)
            ws.write("C%s" % row, int(sku_count), center)
            ws.write("D%s" % row, sale.amount_total, center)
            sum_sale_amount += sale.amount_total
            cogs = 0
            deduct_cogs = 0
            deduct_cogs_usd = 0
            product_qty = 0
            for line in sale.order_line:
                if line.product_id.detailed_type == "product":
                    if data["form"]["cost_percentage"]:
                        cost = (line.product_id.standard_price * data["form"]["cost_percentage"]) / 100
                        cogs += (cost + line.product_id.standard_price) * line.product_uom_qty
                    else:
                        cogs += line.product_id.standard_price * line.product_uom_qty
                    product_qty += line.product_uom_qty
                    if line.price_unit == 0.00:
                        deduct_cogs += line.product_id.standard_price
                        deduct_cogs_usd += deduct_cogs * 1.09
                    if deduct_cogs:
                        cogs -= deduct_cogs
            total_profit = 0
            picking_packing_cost = sale.company_id.picking_packing_cost if (sku_count > 0) else 0
            additional_pick_pack = 0
            if sku_count > sale.company_id.min_pick_pack_cost_upto_sku_count:
                additional_pick_pack = sku_count - sale.company_id.min_pick_pack_cost_upto_sku_count
            additional_pick_pack_cost = additional_pick_pack * sale.company_id.additional_picking_packing_cost
            picking_packing_cost += additional_pick_pack_cost
            payment_method_code_record = self.env["payment.method.code"].search(
                [("workflow_id", "=", sale.auto_workflow_process_id.id)], limit=1
            )
            shipping_charge = (
                sale.company_id.barneys_payment_surcharge and sale.company_id.barneys_payment_surcharge or 0.00
            )
            payment_surcharge = payment_method_code_record.payment_charge if payment_method_code_record else 0
            payment_charge_amt = ((sale.amount_total * payment_surcharge) / 100) + 0.29
            cogs_usd = cogs * 1.09
            total_profit = sale.amount_total - payment_charge_amt - picking_packing_cost - cogs_usd - shipping_charge
            total_profit_percentage = ((total_profit / sale.amount_total) * 100) if (sale.amount_total > 0) else 0
            ws.write("E%s" % row, round(cogs, 2), center)
            ws.write("F%s" % row, round(cogs_usd, 2), center)
            sum_cogs += cogs
            sum_cogs_usd += cogs_usd
            ws.write("G%s" % row, f"{round(deduct_cogs,2)}", center)
            amount_to_be_collected = sale.invoice_ids and sale.invoice_ids[0].amount_to_be_collected or 0.00
            total_amount_to_be_collected += amount_to_be_collected
            ws.write("H%s" % row, round(deduct_cogs_usd, 2), center)
            ws.write("I%s"%row,amount_to_be_collected,center)
            sum_deduct_cogs += deduct_cogs
            sum_deduct_cogs_usd += deduct_cogs_usd
            sum_tax += sale.amount_tax
            ws.write("J%s" % row, shipping_charge, center)
            sum_shipping_charge += shipping_charge
            stamps = sum(sale.picking_ids.filtered(lambda pick: pick.state == "done").mapped("stamps_shipping_rate"))
            ws.write("K%s" % row, stamps, center)
            sum_stamps += stamps

            ws.write("L%s" % row, round(payment_charge_amt, 2), center)

            sum_payment_surcharge += payment_charge_amt
            ws.write("M%s" % row, round(picking_packing_cost, 2), center)
            sum_picking_cost += picking_packing_cost
            ws.write("N%s" % row, f"{round(total_profit_percentage,2)}%", center)
            ws.write("O%s" % row, round(total_profit, 2), center)
            sum_profit += total_profit
            tgr_percentage = 0
            config_tgr_percentage = sale.company_id.tgr_percentage
            tgr_percentage = (float(config_tgr_percentage) / 100) * total_profit
            barneys_percentage = 0
            config_barneys_percentage = sale.company_id.barneys_percentage
            barneys_percentage = (float(config_barneys_percentage) / 100) * total_profit
            ws.write("P%s" % row, round(tgr_percentage, 2) if tgr_percentage else "", center)
            sum_tgr_profit += tgr_percentage
            ws.write("Q%s" % row, round(barneys_percentage, 2) if barneys_percentage else "", center)
            sum_barneys_profit += barneys_percentage
            row += 1

        ws.write("D%s" % row, round(sum_sale_amount, 2), total_format)
        ws.write("E%s" % row, round(sum_cogs, 2), total_format)
        ws.write("F%s" % row, round(sum_cogs_usd, 2), total_format)
        ws.write("G%s" % row, round(sum_deduct_cogs, 2), total_format)
        ws.write("H%s" % row, round(sum_deduct_cogs_usd, 2), total_format)
        ws.write("I%s" % row, round(total_amount_to_be_collected, 2), total_format)
        # ws.write("J%s" % row, round(sum_tax, 2), total_format)
        ws.write("J%s" % row, round(sum_shipping_charge, 2), total_format)
        ws.write("K%s" % row, round(sum_stamps, 2), total_format)
        ws.write("L%s" % row, round(sum_payment_surcharge, 2), total_format)
        ws.write("M%s" % row, round(sum_picking_cost, 2), total_format)
        # ws.write"L%s" % row, round(sum_tax,2), total_format)
        ws.write("O%s" % row, round(sum_profit, 2), total_format)
        ws.write("P%s" % row, round(sum_tgr_profit, 2), total_format)
        ws.write("Q%s" % row, round(sum_barneys_profit, 2), total_format)

        ws2 = workbook.add_worksheet("Barney's Split Up Report")

        ws2.merge_range("A1:D1", "Barney's Report", boldl)
        ws2.write("A3", "Start Date", boldl)
        ws2.write("A4", "End Date", boldl)
        ws2.write("B3", start_date.strftime("%d-%m-%Y"), center)
        ws2.write("B4", end_date.strftime("%d-%m-%Y"), center)

        ws2.set_column("A:A", 20)
        ws2.set_column("B:B", 20)
        ws2.set_column("C:C", 20)
        ws2.set_column("D:D", 20)
        ws2.set_column("E:E", 20)
        ws2.set_column("F:F", 20)
        ws2.set_column("G:G", 20)
        ws2.set_column("H:H", 20)
        ws2.set_column("I:I", 20)
        ws2.set_column("J:J", 20)

        row = 6

        ws2.write("A%s" % row, "Order No", boldc)
        ws2.write("B%s" % row, "Order Date", boldc)
        ws2.write("C%s" % row, "Product", boldc)
        ws2.write("D%s" % row, "Qty", boldc)
        ws2.write("E%s" % row, "Sales Price", boldc)
        ws2.write("F%s" % row, "Total", boldc)
        ws2.write("G%s" % row, "Cost", boldc)
        ws2.write("H%s" % row, "Total Cost", boldc)
        ws2.write("I%s" % row, "Tax", boldc)

        row = 7
        sale_order_ids = self.env["sale.order"].search(
            [
                ("date_order", ">=", start_date),
                ("date_order", "<=", end_date),
                ("state", "=", "sale"),
                ("is_barneys_dropshipping", "=", True),
            ]
        )

        sum_sale_amount = 0
        sum_cost = 0
        sum_total = 0
        sum_tax = 0
        for line in sale_order_ids.order_line:
            ws2.write("A%s" % row, line.order_id.name, center)
            ws2.write("B%s" % row, line.order_id.date_order.strftime("%d-%m-%Y"), center)
            ws2.write("C%s" % row, line.product_id.name, center)
            ws2.write("D%s" % row, line.product_uom_qty, center)
            ws2.write("E%s" % row, line.price_unit, center)
            ws2.write("F%s" % row, line.price_subtotal, center)
            sum_sale_amount += line.price_subtotal
            cost = 0
            additional_cost = 0
            if data["form"]["cost_percentage"]:
                cost = (line.product_id.standard_price * data["form"]["cost_percentage"]) / 100
                additional_cost = cost + line.product_id.standard_price
            else:
                additional_cost = line.product_id.standard_price
            ws2.write("G%s" % row, additional_cost, center)
            sum_cost += additional_cost
            total_cost = 0
            total_cost = line.product_uom_qty * additional_cost
            sum_total += total_cost
            ws2.write("H%s" % row, total_cost, center)
            ws2.write("I%s" % row, line.price_tax, center)
            sum_tax += line.price_tax
            row += 1

        ws2.write("F%s" % row, sum_sale_amount, total_format)
        ws2.write("G%s" % row, sum_cost, total_format)
        ws2.write("H%s" % row, sum_total, total_format)
        ws2.write("I%s" % row, sum_tax, total_format)
