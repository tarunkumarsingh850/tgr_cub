from odoo import models
from datetime import datetime


class DropshippingReport(models.AbstractModel):
    _name = "report.bi_dropshipping_report.generate_drop_shipping_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        ws = workbook.add_worksheet("Drop Shipping Report")
        boldl = workbook.add_format({"bold": True, "align": "left"})
        boldr = workbook.add_format({"bold": True, "align": "right"})
        boldc = workbook.add_format({"bold": True, "align": "center", "bg_color": "#808080", "color": "#ffffff"})
        center = workbook.add_format({"align": "center"})
        right = workbook.add_format({"align": "right"})
        total_format = workbook.add_format({"bold": True, "align": "center"})

        # WIZARD VALUES
        start_date = data["form"]["start_date"]
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = data["form"]["end_date"]
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        partner_id = self.env["res.partner"].search([("id", "=", int(data["form"]["partner_id"]))])

        ws.merge_range("A1:D1", "Drop Shipping Report", boldl)
        ws.write("A3", "Customer", boldl)
        ws.merge_range("B3:C3", partner_id.name, center)
        ws.write("E3", "Start Date", boldl)
        ws.write("E4", "End Date", boldl)
        ws.write("F3", start_date.strftime("%d-%m-%Y"), center)
        ws.write("F4", end_date.strftime("%d-%m-%Y"), center)

        ws.set_column("A:A", 20)
        ws.set_column("B:B", 20)
        ws.set_column("C:C", 20)
        ws.set_column("D:D", 20)
        ws.set_column("E:E", 25)
        ws.set_column("F:F", 22)
        ws.set_column("G:G", 20)

        row = 6

        ws.write("A%s" % row, "Order No", boldc)
        ws.write("B%s" % row, "Order Date", boldc)
        ws.write("C%s" % row, "Sale Total Amount", boldc)
        ws.write("D%s" % row, "COGS", boldc)
        ws.write("E%s" % row, "Purchase Price", boldc)
        ws.write("F%s" % row, "Picking and Packing Cost", boldc)
        ws.write("G%s" % row, "US Shipping Cost", boldc)

        sale_order_ids = self.env["sale.order"].search(
            [
                ("date_order", ">=", start_date),
                ("date_order", "<=", end_date),
                ("state", "=", "sale"),
                ("is_drop_shipping", "=", True),
            ]
        )

        row = 7
        total_sale_amount = 0
        total_cogs_old_revert = 0
        total_cogs = 0
        total_pick_pack = 0
        total_shipping = 0
        for sale in sale_order_ids:
            ws.write("A%s" % row, sale.name, center)
            ws.write("B%s" % row, sale.date_order.strftime("%d-%m-%Y"), center)
            ws.write("C%s" % row, round(sale.amount_total, 2), right)
            total_sale_amount += sale.amount_total
            cogs = 0
            cogs_old_revert = 0
            product_qty = 0
            shipping_cost = sale.company_id.dropshipping_shipping_cost
            for line in sale.order_line:
                if line.product_id.detailed_type == "product":
                    product_price = partner_id.property_product_pricelist.item_ids.filtered(
                        lambda pl: pl.product_tmpl_id == line.product_id.product_tmpl_id
                    ).fixed_price
                    if data["form"]["cost_percentage"]:
                        cost_old_revert = (line.product_id.standard_price * data["form"]["cost_percentage"]) / 100
                        cogs_old_revert += (cost_old_revert + line.product_id.standard_price) * line.product_uom_qty

                        cost = (product_price * data["form"]["cost_percentage"]) / 100
                        cogs += (cost + product_price) * line.product_uom_qty
                    else:
                        cogs_old_revert += line.product_id.standard_price * line.product_uom_qty
                        cogs += product_price * line.product_uom_qty
                    product_qty += line.product_uom_qty
            sku_count = len(sale.order_line.filtered(lambda line: line.product_id.detailed_type == "product"))
            picking_packing_cost = sale.company_id.dropshipping_picking_packing_cost if (sku_count > 0) else 0
            additional_pick_pack = 0
            if sku_count > sale.company_id.dropshipping_min_pick_pack_cost_upto_sku_count:
                additional_pick_pack = sku_count - sale.company_id.dropshipping_min_pick_pack_cost_upto_sku_count
            additional_pick_pack_cost = (
                additional_pick_pack * sale.company_id.dropshipping_additional_picking_packing_cost
            )
            picking_packing_cost += additional_pick_pack_cost
            ws.write("D%s" % row, round(cogs_old_revert, 2), right)
            total_cogs_old_revert += cogs_old_revert
            ws.write("E%s" % row, round(cogs, 2), right)
            total_cogs += cogs
            ws.write("F%s" % row, round(picking_packing_cost, 2), right)
            total_pick_pack += picking_packing_cost
            ws.write("G%s" % row, round(shipping_cost, 2), right)
            total_shipping += shipping_cost
            row += 1
        ws.merge_range(f"A{row}:B{row}", "TOTAL", boldc)
        ws.write(f"C{row}", round(total_sale_amount, 2), boldr)
        ws.write(f"D{row}", round(total_cogs_old_revert, 2), boldr)
        ws.write(f"E{row}", round(total_cogs, 2), boldr)
        ws.write(f"F{row}", round(total_pick_pack, 2), boldr)
        ws.write(f"G{row}", round(total_shipping, 2), boldr)

        ws2 = workbook.add_worksheet("Drop Shipping's Split Up Report")

        ws2.merge_range("A1:D1", "Drop Shipping's Report", boldl)
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
        ws2.write("F%s" % row, "Cost", boldc)
        ws2.write("G%s" % row, "Purchase Price", boldc)
        # ws2.write("H%s" % row, "Total Cost", boldc)
        # ws2.write("I%s" % row, "Tax", boldc)

        row = 7
        sale_order_ids = self.env["sale.order"].search(
            [
                ("date_order", ">=", start_date),
                ("date_order", "<=", end_date),
                ("state", "=", "sale"),
                ("is_drop_shipping", "=", True),
            ]
        )

        for line in sale_order_ids.order_line:
            cost1 = 0
            cogs = 0
            if line.product_id.detailed_type == "product":
                product_price = lines.partner_id.property_product_pricelist.item_ids.filtered(
                    lambda pl: pl.product_tmpl_id == line.product_id.product_tmpl_id
                ).fixed_price
                if lines.cost_percentage:
                    cost1 = (product_price * lines.cost_percentage) / 100
                    cogs = (cost1 + product_price) * line.product_uom_qty
                else:
                    cogs = product_price * line.product_uom_qty

            ws2.write("A%s" % row, line.order_id.name, center)
            ws2.write("B%s" % row, line.order_id.date_order.strftime("%d-%m-%Y"), center)
            ws2.write("C%s" % row, line.product_id.name, center)
            ws2.write("D%s" % row, line.product_uom_qty, center)
            ws2.write("E%s" % row, line.price_unit, center)
            ws2.write("F%s" % row, line.product_id.standard_price, center)
            ws2.write("G%s" % row, cogs, center)
            # sum_sale_amount += line.price_subtotal
            # cost = 0
            # additional_cost = 0
            # if data["form"]["cost_percentage"]:
            #     cost = (line.product_id.standard_price  * data["form"]["cost_percentage"]) /100
            #     additional_cost = cost + line.product_id.standard_price
            # else:
            #     additional_cost = line.product_id.standard_price
            # ws2.write("H%s" % row, additional_cost, center)
            # sum_cost += additional_cost
            # total_cost = 0
            # total_cost = line.product_uom_qty * additional_cost
            # sum_total += total_cost
            # ws2.write("I%s" % row,total_cost, center)
            # ws2.write("J%s" % row,line.price_tax, center)
            # sum_tax += line.price_tax
            row += 1

        # ws2.write("F%s" % row,round(sum_sale_amount,2), total_format)
        # ws2.write("G%s" % row,round(sum_cost,2), total_format)
        # ws2.write("I%s" % row,round(sum_total,2), total_format)
        # ws2.write("J%s" % row,round(sum_tax,2), total_format)
