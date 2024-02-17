from odoo import models, fields
from datetime import timedelta
import string


class ReplenishmentReportXlsx(models.AbstractModel):
    _name = "report.bi_replenishment_report.report_replenishment_xlsx"
    _description = "Replenishment XLSX Report"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Replenishment Report")
        format1_header = workbook.add_format({"bold": True, "align": "center", "valign": "vcenter", "border": 1})
        format4_title = workbook.add_format({"bold": True, "align": "center", "font_size": 24, "border": 1})
        format5 = workbook.add_format({"align": "right", "valign": "vcenter", "text_wrap": True, "bg_color": "red"})
        format5_l = workbook.add_format({"align": "left", "valign": "vcenter", "text_wrap": True, "bg_color": "red"})
        format6 = workbook.add_format({"align": "right", "valign": "vcenter", "text_wrap": True})
        format6_l = workbook.add_format({"align": "left", "valign": "vcenter", "text_wrap": True})
        worksheet.set_row(0, 30)
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
        worksheet.set_column("K:K", 20)
        worksheet.set_column("L:L", 20)
        worksheet.set_column("M:M", 20)
        worksheet.set_column("N:N", 20)
        worksheet.set_column("O:O", 20)
        worksheet.set_column("P:P", 20)
        worksheet.set_column("Q:Q", 20)
        worksheet.set_column("R:R", 20)
        worksheet.set_column("S:S", 20)
        worksheet.set_column("T:T", 20)
        worksheet.set_column("U:U", 25)
        worksheet.set_column("V:V", 25)
        worksheet.set_column("W:W", 25)
        worksheet.set_column("X:X", 25)
        worksheet.set_column("Y:Y", 25)
        worksheet.set_column("Z:Z", 25)
        worksheet.set_column("AA:AA", 25)
        worksheet.set_column("AB:AB", 25)
        worksheet.set_column("AC:AC", 25)
        worksheet.set_column("AD:AD", 25)
        worksheet.set_column("AE:AE", 25)
        worksheet.set_column("AF:AF", 25)
        worksheet.set_column("AG:AG", 25)
        worksheet.set_column("AH:AH", 25)
        worksheet.set_column("AI:AI", 25)

        worksheet.merge_range("A1:W1", "Replenishment Report", format4_title)
        letters = list(string.ascii_uppercase)
        big_letters = list(string.ascii_uppercase)
        for a in letters:
            for b in letters:
                big_letters.append("{}{}".format(a, b))
        letters = big_letters
        row = 2
        col_no = 0
        next_col = 0
        avg_weeks = data["form"]["avg_weeks"]
        for i in range(1, avg_weeks + 1):
            worksheet.write("{}{}".format(letters[col_no], row), i, format1_header)
            col_no += 1
        current_col = col_no
        worksheet.write("{}{}".format(letters[current_col], row), "Av.", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 1], row), "Phys.", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 2], row), "Alloc.", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 3], row), "On.ord.", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 4], row), "Ideal", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 5], row), "Avail", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 6], row), "Order Qty.", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 7], row), "Product", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 8], row), "Tax Category", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 9], row), "Warehouse", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 10], row), "Inventory ID", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 11], row), "Supplier", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 12], row), "Supplier SKU", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 13], row), "Breeder", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 14], row), "Exclude from customers", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 15], row), "Case Qty.", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 16], row), "Pending Discontinued", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 17], row), "Wsale €", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 18], row), "Retail €", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 19], row), "Cost €", format1_header)
        warehouse = data["form"]["warehouse_id"]
        flower_type_id = data["form"]["flower_type_id"]
        sex_id = data["form"]["sex_id"]
        size_id = data["form"]["size_id"]
        brand_breeder_id = data["form"]["brand_breeder_id"]
        avg_weeks_for_sale = data["form"]["avg_weeks_for_sale"]
        domain = []
        if flower_type_id:
            domain.append(("flower_type_id", "=", flower_type_id))
        if sex_id:
            domain.append(("product_sex_id", "=", sex_id))
        if size_id:
            domain.append(("product_size_id", "=", size_id))
        if brand_breeder_id:
            domain.append(("product_breeder_id", "=", brand_breeder_id))

        all_product_ids = self.env["product.product"].search(domain)
        product_ids = (
            self.env["stock.warehouse.orderpoint"]
            .search([("product_id", "in", all_product_ids.ids), ("warehouse_id", "=", warehouse)])
            .mapped("product_id")
        )
        warehouse_id = self.env["stock.warehouse"].search([("id", "=", warehouse)])
        row += 1
        for product in product_ids:
            col_no = 0
            today_date = fields.Date.today()
            total_delivered_quantity = 0
            for i in range(avg_weeks, 0, -1):
                start_period_date = today_date - timedelta(days=i * 7)
                end_period_date = start_period_date + timedelta(days=7)
                qty_delivered = 0
                sale_line_ids = self.env["sale.order.line"].search(
                    [
                        ("product_id", "=", product.id),
                        ("order_id.state", "in", ("done", "sale")),
                        ("order_id.date_order", ">=", start_period_date),
                        ("order_id.date_order", "<=", end_period_date),
                    ]
                )
                qty_delivered = sum(sale_line_ids.mapped("quantity"))
                if product.is_out_of_stock:
                    worksheet.write(
                        "{}{}".format(letters[col_no], row), qty_delivered if qty_delivered else "0", format5
                    )
                else:
                    worksheet.write(
                        "{}{}".format(letters[col_no], row), qty_delivered if qty_delivered else "0", format6
                    )
                col_no += 1
                total_delivered_quantity += qty_delivered
                next_col = col_no
            qty_onhand = product.with_context({"location": warehouse_id.lot_stock_id.id}).qty_available
            outgoing_move_ids = self.env["stock.move"].search(
                [
                    ("product_id", "=", product.id),
                    ("location_id", "=", warehouse_id.lot_stock_id.id),
                    ("picking_id.picking_type_code", "=", "outgoing"),
                ]
            )
            sale_reserved_qty = sum(outgoing_move_ids.mapped("forecast_availability"))
            incoming_move_ids = self.env["stock.move"].search(
                [
                    ("product_id", "=", product.id),
                    ("location_id", "=", warehouse_id.lot_stock_id.id),
                    ("picking_id.picking_type_code", "=", "incoming"),
                ]
            )
            purchase_reserved_qty = sum(incoming_move_ids.mapped("reserved_availability"))
            free_quantity = product.with_context({"location": warehouse_id.lot_stock_id.id}).free_qty
            tax_category_ids = product.tag_groups_ids
            product_tax_categories = ",".join(tax_category_ids.mapped("name"))
            supplier = product.seller_ids[0].display_name if product.seller_ids else ""
            average = (total_delivered_quantity / avg_weeks) if avg_weeks else 0
            ideal_qty = average * avg_weeks_for_sale
            order_qty = ideal_qty - qty_onhand - sale_reserved_qty - purchase_reserved_qty
            if product.is_out_of_stock:
                worksheet.write(
                    "{}{}".format(letters[next_col], row),
                    "{:.2f}".format(total_delivered_quantity / avg_weeks) if total_delivered_quantity else "0",
                    format5,
                )
                worksheet.write("{}{}".format(letters[next_col + 1], row), qty_onhand if qty_onhand else "0", format5)
                worksheet.write(
                    "{}{}".format(letters[next_col + 2], row), sale_reserved_qty if sale_reserved_qty else "0", format5
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 3], row),
                    purchase_reserved_qty if purchase_reserved_qty else "0",
                    format5,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 4], row),
                    "{:.2f}".format(ideal_qty) if ideal_qty else "0",
                    format5,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 5], row), free_quantity if free_quantity else "0", format5
                )
                worksheet.write("{}{}".format(letters[next_col + 6], row), "{:.2f}".format(order_qty), format5)
                worksheet.write("{}{}".format(letters[next_col + 7], row), product.name, format5_l)
                worksheet.write("{}{}".format(letters[next_col + 8], row), product_tax_categories, format5_l)
                worksheet.write(
                    "{}{}".format(letters[next_col + 9], row), warehouse_id.name if warehouse_id else "", format5_l
                )
                worksheet.write("{}{}".format(letters[next_col + 10], row), product.default_code, format5_l)
                worksheet.write("{}{}".format(letters[next_col + 11], row), supplier, format5_l)
                worksheet.write(
                    "{}{}".format(letters[next_col + 12], row),
                    product.supplier_sku_no if product.supplier_sku_no else "0",
                    format5,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 13], row),
                    product.product_breeder_id.breeder_name if product.product_breeder_id else "",
                    format5_l,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 14], row),
                    "Yes" if product.is_excluded_customer else "No",
                    format5_l,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 15], row),
                    product.case_quantity if product.case_quantity else "0",
                    format5,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 16], row),
                    "Yes" if product.is_pending_discontinued else "No",
                    format5_l,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 17], row),
                    product.wholesale_price_value if product.wholesale_price_value else "0",
                    format5,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 18], row),
                    product.retail_default_price if product.retail_default_price else "0",
                    format5,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 19], row), product.last_cost if product.last_cost else "0", format5
                )
                row += 1
            else:
                worksheet.write(
                    "{}{}".format(letters[next_col], row),
                    "{:.2f}".format(total_delivered_quantity / avg_weeks) if total_delivered_quantity else "0",
                    format6,
                )
                worksheet.write("{}{}".format(letters[next_col + 1], row), qty_onhand if qty_onhand else "0", format6)
                worksheet.write(
                    "{}{}".format(letters[next_col + 2], row), sale_reserved_qty if sale_reserved_qty else "0", format6
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 3], row),
                    purchase_reserved_qty if sale_reserved_qty else "0",
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 4], row),
                    "{:.2f}".format(ideal_qty) if ideal_qty else "0",
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 5], row), free_quantity if free_quantity else "0", format6
                )
                worksheet.write("{}{}".format(letters[next_col + 6], row), "{:.2f}".format(order_qty), format6)
                worksheet.write("{}{}".format(letters[next_col + 7], row), product.name, format6_l)
                worksheet.write("{}{}".format(letters[next_col + 8], row), product_tax_categories, format6_l)
                worksheet.write(
                    "{}{}".format(letters[next_col + 9], row), warehouse_id.name if warehouse_id else "", format6_l
                )
                worksheet.write("{}{}".format(letters[next_col + 10], row), product.default_code, format6_l)
                worksheet.write("{}{}".format(letters[next_col + 11], row), supplier, format6_l)
                worksheet.write(
                    "{}{}".format(letters[next_col + 12], row),
                    product.supplier_sku_no if product.supplier_sku_no else "0",
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 13], row),
                    product.product_breeder_id.breeder_name if product.product_breeder_id else "",
                    format6_l,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 14], row),
                    "Yes" if product.is_excluded_customer else "No",
                    format6_l,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 15], row),
                    product.case_quantity if product.case_quantity else "0",
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 16], row),
                    "Yes" if product.is_pending_discontinued else "No",
                    format6_l,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 17], row),
                    product.wholesale_price_value if product.wholesale_price_value else "0",
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 18], row),
                    product.retail_default_price if product.retail_default_price else "0",
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 19], row), product.last_cost if product.last_cost else "0", format6
                )
                row += 1
