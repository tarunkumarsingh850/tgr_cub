from odoo import models, fields
from datetime import timedelta, date
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
        format7 = workbook.add_format({"align": "right", "valign": "vcenter", "text_wrap": True, "bg_color": "#45b6fe"})
        format7_l = workbook.add_format(
            {"align": "left", "valign": "vcenter", "text_wrap": True, "bg_color": "#45b6fe"}
        )
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
        worksheet.set_column("AJ:AJ", 25)

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
        worksheet.write("{}{}".format(letters[current_col + 1], row), "Lead Time", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 2], row), "Phys.", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 3], row), "Alloc.", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 4], row), "On.ord.", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 5], row), "Ideal", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 6], row), "Avail", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 7], row), "Order Qty.", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 8], row), "Order Qty + Lead Time", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 9], row), "Product", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 10], row), "Created On", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 11], row), "Tax Category", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 12], row), "Warehouse", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 13], row), "Inventory ID", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 14], row), "Supplier", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 15], row), "Supplier SKU", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 16], row), "Breeder", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 17], row), "Exclude from customers", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 18], row), "Case Qty.", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 19], row), "Pending Discontinued", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 20], row), "Wsale €", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 21], row), "Retail €", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 22], row), "Cost €", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 23], row), "Product Tag", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 24], row), "Product Category", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 25], row), "Last Purchase Order", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 26], row), "Last Receipt Date", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 27], row), "Order Qty Same Period Previous Year", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 28], row), "Total Sale Qty", format1_header)
        worksheet.write("{}{}".format(letters[current_col + 29], row), "Order Quantity Next Week", format1_header)
        warehouse = data["form"]["warehouse_id"]
        flower_type_id = data["form"]["flower_type_id"]
        sex_id = data["form"]["sex_id"]
        size_id = data["form"]["size_id"]
        brand_breeder_id = data["form"]["brand_breeder_id"]
        avg_weeks_for_sale = data["form"]["avg_weeks_for_sale"]
        lead_time_in_weeks = data["form"]["lead_time_in_weeks"]

        current_date = date.today()
        years_to_minus = current_date.year - 1

        date_1 = current_date
        date_2 = current_date.replace(year=years_to_minus)

        days = abs(date_1-date_2).days

        avg_weeks_for_sale_in_year = days//7

        domain = []
        domain.append(("is_exclude_from_replenishment", "=", False))
        if flower_type_id:
            domain.append(("flower_type_id", "=", flower_type_id))
        if sex_id:
            domain.append(("product_sex_id", "=", sex_id))
        if size_id:
            domain.append(("product_size_id", "=", size_id))
        if brand_breeder_id:
            domain.append(("product_breeder_id", "in", brand_breeder_id))

        self.env["product.product"].search(domain)
        # product_ids = (
        #     self.env["stock.warehouse.orderpoint"]
        #     .search([("product_id", "in", all_product_ids.ids), ("warehouse_id", "=", warehouse)])
        #     .mapped("product_id")
        # )
        warehouse_id = self.env["stock.warehouse"].search([("id", "=", warehouse)])
        if warehouse_id.code == "MALAG":
            domain.append(("is_malaga_replenishment", "=", True))
        elif warehouse_id.code == "UKBAR":
            domain.append(("is_uk_replenishment", "=", True))
        elif warehouse_id.code == "UK3PL":
            domain.append(("is_uk_replenishment", "=", True))
        elif warehouse_id.code == "USLIV":
            domain.append(("is_usa_replenishment", "=", True))
        product_ids = self.env["product.template"].search(domain)

        row += 1
        for product in product_ids:
            if product.is_pending_discontinued:
                format5 = workbook.add_format({"align": "right", "valign": "vcenter", "text_wrap": True, "bg_color": "#10f500"})
                format5_l = workbook.add_format({"align": "left", "valign": "vcenter", "text_wrap": True, "bg_color": "#10f500"})
                format6 = workbook.add_format({"align": "right", "valign": "vcenter", "text_wrap": True, "bg_color": "#10f500"})
                format6_l = workbook.add_format({"align": "left", "valign": "vcenter", "text_wrap": True,"bg_color": "#10f500"})
                format7 = workbook.add_format({"align": "right", "valign": "vcenter", "text_wrap": True, "bg_color": "#10f500"})
                format7_l = workbook.add_format(
                    {"align": "left", "valign": "vcenter", "text_wrap": True, "bg_color": "#10f500"}
                )

            else:
                format5 = workbook.add_format({"align": "right", "valign": "vcenter", "text_wrap": True, "bg_color": "red"})
                format5_l = workbook.add_format({"align": "left", "valign": "vcenter", "text_wrap": True, "bg_color": "red"})
                format6 = workbook.add_format({"align": "right", "valign": "vcenter", "text_wrap": True})
                format6_l = workbook.add_format({"align": "left", "valign": "vcenter", "text_wrap": True})
                format7 = workbook.add_format({"align": "right", "valign": "vcenter", "text_wrap": True, "bg_color": "#45b6fe"})
                format7_l = workbook.add_format(
                    {"align": "left", "valign": "vcenter", "text_wrap": True, "bg_color": "#45b6fe"}
                )
                
                
            date_of_receipt = product.date_of_receipt + timedelta(hours=5, minutes=30, seconds=29) if product.date_of_receipt else ""
            product_id = self.env["product.product"].search([("product_tmpl_id", "=", product.id)], limit=1)
            col_no = 0
            today_date = fields.Date.today()
            today = date.today()
            product_created_date = product.create_date.date()
            product_days = int(
                self.env["ir.config_parameter"].sudo().get_param("bi_inventory_generic_customisation.product_days")
            )
            total_delivered_quantity = 0
            product_qty_delived = 0
            for i in range(avg_weeks, 0, -1):
                start_period_date = today_date - timedelta(days=i * 7)
                end_period_date = start_period_date + timedelta(days=6)
                qty_delivered = 0
                sale_line_ids = self.env["sale.order.line"].search(
                    [
                        ("product_id", "=", product_id.id),
                        ("order_id.state", "in", ("done", "sale")),
                        ("order_id.date_order", ">=", start_period_date),
                        ("order_id.date_order", "<=", end_period_date),
                        ("order_id.warehouse_id", "=", warehouse),
                    ]
                )
                qty_delivered = round(sum(sale_line_ids.mapped("qty_delivered")), 2)
                product_qty_delived += qty_delivered
                if product_id.is_out_of_stock:
                    worksheet.write(
                        "{}{}".format(letters[col_no], row), qty_delivered if qty_delivered else "0", format5
                    )
                elif product_created_date >= today - timedelta(days=product_days):
                    worksheet.write(
                        "{}{}".format(letters[col_no], row), qty_delivered if qty_delivered else "0", format7
                    )
                else:
                    worksheet.write(
                        "{}{}".format(letters[col_no], row), qty_delivered if qty_delivered else "0", format6
                    )
                col_no += 1
                total_delivered_quantity += qty_delivered
                next_col = col_no
            qty_onhand = product_id.with_context({"location": warehouse_id.lot_stock_id.id}).qty_available
            outgoing_move_ids = self.env["stock.move"].search(
                [
                    ("product_id", "=", product_id.id),
                    ("location_id", "=", warehouse_id.lot_stock_id.id),
                    ("picking_id.picking_type_code", "=", "outgoing"),
                ]
            )
            sale_reserved_qty = sum(outgoing_move_ids.mapped("forecast_availability"))
            purchase_order_ids = (
                self.env["purchase.order"]
                .sudo()
                .search(
                    [
                        ("picking_type_id.default_location_dest_id", "=", warehouse_id.lot_stock_id.id),
                        ("is_created_picking", "=", False),
                        ("state", "in", ("done", "purchase")),
                        ("company_id", "=", warehouse_id.company_id.id),
                    ]
                )
            )

            # incoming_move_ids = self.env["stock.move"].search(
            #     [
            #         ("product_id", "=", product.id),
            #         ("location_id", "=", warehouse_id.lot_stock_id.id),
            #         ("picking_id.picking_type_code", "=", "incoming"),
            #     ]
            # )
            # purchase_reserved_qty = sum(incoming_move_ids.mapped("reserved_availability"))
            purchase_reserved_qty = sum(
                purchase_order_ids.mapped("order_line")
                .filtered(lambda line: line.product_id == product_id)
                .mapped("product_qty")
            )
            free_quantity = product_id.with_context({"location": warehouse_id.lot_stock_id.id}).free_qty
            free_quantity + purchase_reserved_qty
            tax_category_ids = product_id.tag_groups_ids
            product_tax_categories = ",".join(tax_category_ids.mapped("name"))
            supplier = product.seller_ids[0].display_name if product_id.seller_ids else ""
            average = (total_delivered_quantity / avg_weeks) if avg_weeks else 0
            ideal_qty = round(average * avg_weeks_for_sale)
            ideal_qty_in_year = round(average * avg_weeks_for_sale_in_year)
            # order_qty = round((ideal_qty - avail_qty))
            lead_time = round(average * (lead_time_in_weeks if lead_time_in_weeks else 0.00), 2)

            order_qty = round((ideal_qty - free_quantity) - purchase_reserved_qty)
            order_qty_in_year = round((ideal_qty_in_year - free_quantity) - purchase_reserved_qty)
            sale_start_date = date(2023, 1, 1)
            total_weeks = int((today - sale_start_date).days/7)
            order_qty_week = round((product_qty_delived/total_weeks)*avg_weeks_for_sale,0)
            if product_id.is_out_of_stock:
                worksheet.write(
                    "{}{}".format(letters[next_col], row),
                    "{:.2f}".format(total_delivered_quantity / avg_weeks) if total_delivered_quantity else "0",
                    format5,
                )
                worksheet.write("{}{}".format(letters[next_col + 1], row), lead_time if lead_time else "0", format5)
                worksheet.write("{}{}".format(letters[next_col + 2], row), qty_onhand if qty_onhand else "0", format5)
                worksheet.write(
                    "{}{}".format(letters[next_col + 3], row), sale_reserved_qty if sale_reserved_qty else "0", format5
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 4], row),
                    purchase_reserved_qty if purchase_reserved_qty else "0",
                    format5,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 5], row),
                    ideal_qty if ideal_qty else "0",
                    format5,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 6], row), free_quantity if free_quantity else "0", format5
                )
                worksheet.write("{}{}".format(letters[next_col + 7], row), order_qty, format5)
                worksheet.write("{}{}".format(letters[next_col + 8], row), order_qty + lead_time, format5)
                worksheet.write("{}{}".format(letters[next_col + 9], row), product.name, format5_l)
                worksheet.write(
                    "{}{}".format(letters[next_col + 10], row), product.create_date.strftime("%d-%m-%Y"), format5_l
                )
                worksheet.write("{}{}".format(letters[next_col + 11], row), product_tax_categories, format5_l)
                worksheet.write(
                    "{}{}".format(letters[next_col + 12], row), warehouse_id.name if warehouse_id else "", format5_l
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 13], row),
                    product.default_code if product.default_code else "",
                    format5_l,
                )
                worksheet.write("{}{}".format(letters[next_col + 14], row), supplier, format5_l)
                worksheet.write(
                    "{}{}".format(letters[next_col + 15], row),
                    product.supplier_sku_no if product.supplier_sku_no else "",
                    format5,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 16], row),
                    product.product_breeder_id.breeder_name if product.product_breeder_id else "",
                    format5_l,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 17], row),
                    "Yes" if product.is_excluded_customer else "No",
                    format5_l,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 18], row),
                    product.case_quantity if product.case_quantity else "0",
                    format5,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 19], row),
                    "Yes" if product.is_pending_discontinued else "No",
                    format5_l,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 20], row),
                    product.wholesale_price_value if product.wholesale_price_value else "0",
                    format5,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 21], row),
                    product.retail_default_price if product.retail_default_price else "0",
                    format5,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 22], row),
                    product.standard_price if product.standard_price else "0",
                    format5,
                )
                product_tag = ""
                for tag in product.product_tag_ids and product.product_tag_ids or "":
                    product_tag += str(tag.name) + ", "
                worksheet.write(
                    "{}{}".format(letters[next_col + 23], row),
                    product_tag,
                    format5,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 24], row),
                    product.categ_id and product.categ_id.name or "",
                    format5,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 26], row),
                    date_of_receipt.strftime("%d-%m-%Y") if date_of_receipt else "",
                    format5,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 27], row), 0,format5)
                worksheet.write(
                    "{}{}".format(letters[next_col + 28], row),product_qty_delived if product_qty_delived else 0,format5)
                worksheet.write(
                    "{}{}".format(letters[next_col + 29], row),order_qty_week if order_qty_week else 0,format5)
                row += 1
            elif product_created_date >= (today - timedelta(days=product_days)):
                worksheet.write(
                    "{}{}".format(letters[next_col], row),
                    "{:.2f}".format(total_delivered_quantity / avg_weeks) if total_delivered_quantity else "0",
                    format7,
                )
                worksheet.write("{}{}".format(letters[next_col + 1], row), lead_time if lead_time else "0", format7)
                worksheet.write("{}{}".format(letters[next_col + 2], row), qty_onhand if qty_onhand else "0", format7)
                worksheet.write(
                    "{}{}".format(letters[next_col + 3], row), sale_reserved_qty if sale_reserved_qty else "0", format7
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 4], row),
                    purchase_reserved_qty if purchase_reserved_qty else "0",
                    format7,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 5], row),
                    ideal_qty if ideal_qty else "0",
                    format7,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 6], row), free_quantity if free_quantity else "0", format7
                )
                worksheet.write("{}{}".format(letters[next_col + 7], row), order_qty, format7)
                worksheet.write("{}{}".format(letters[next_col + 8], row), order_qty + lead_time, format7)
                worksheet.write("{}{}".format(letters[next_col + 9], row), product.name, format7_l)
                worksheet.write(
                    "{}{}".format(letters[next_col + 10], row), product.create_date.strftime("%d-%m-%Y"), format7_l
                )
                worksheet.write("{}{}".format(letters[next_col + 11], row), product_tax_categories, format7_l)
                worksheet.write(
                    "{}{}".format(letters[next_col + 12], row), warehouse_id.name if warehouse_id else "", format7_l
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 13], row),
                    product.default_code if product.default_code else "",
                    format7_l,
                )
                worksheet.write("{}{}".format(letters[next_col + 14], row), supplier, format7_l)
                worksheet.write(
                    "{}{}".format(letters[next_col + 15], row),
                    product.supplier_sku_no if product.supplier_sku_no else "",
                    format7,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 16], row),
                    product.product_breeder_id.breeder_name if product.product_breeder_id else "",
                    format7_l,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 17], row),
                    "Yes" if product.is_excluded_customer else "No",
                    format7_l,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 18], row),
                    product.case_quantity if product.case_quantity else "0",
                    format7,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 19], row),
                    "Yes" if product.is_pending_discontinued else "No",
                    format7_l,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 20], row),
                    product.wholesale_price_value if product.wholesale_price_value else "0",
                    format7,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 21], row),
                    product.retail_default_price if product.retail_default_price else "0",
                    format7,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 22], row),
                    product.standard_price if product.standard_price else "0",
                    format7,
                )
                product_tag = ""
                for tag in product.product_tag_ids and product.product_tag_ids or "":
                    product_tag += str(tag.name) + ", "
                worksheet.write(
                    "{}{}".format(letters[next_col + 23], row),
                    product_tag,
                    format7,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 24], row),
                    product.categ_id and product.categ_id.name or "",
                    format7,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 26], row),
                    date_of_receipt.strftime("%d-%m-%Y") if date_of_receipt else "",
                    format7,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 27], row), 0,format7)
                worksheet.write(
                    "{}{}".format(letters[next_col + 28], row),product_qty_delived if product_qty_delived else 0,format7_l)
                worksheet.write(
                    "{}{}".format(letters[next_col + 29], row),order_qty_week if order_qty_week else 0,format7_l)
                row += 1
            else:
                worksheet.write(
                    "{}{}".format(letters[next_col], row),
                    "{:.2f}".format(total_delivered_quantity / avg_weeks) if total_delivered_quantity else "0",
                    format6,
                )
                worksheet.write("{}{}".format(letters[next_col + 1], row), lead_time if lead_time else "0", format6)
                worksheet.write("{}{}".format(letters[next_col + 2], row), qty_onhand if qty_onhand else "0", format6)
                worksheet.write(
                    "{}{}".format(letters[next_col + 3], row), sale_reserved_qty if sale_reserved_qty else "0", format6
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 4], row),
                    purchase_reserved_qty if purchase_reserved_qty else "0",
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 5], row),
                    ideal_qty if ideal_qty else "0",
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 6], row), free_quantity if free_quantity else "0", format6
                )
                worksheet.write("{}{}".format(letters[next_col + 7], row), order_qty, format6)
                worksheet.write("{}{}".format(letters[next_col + 8], row), order_qty + lead_time, format6)
                worksheet.write("{}{}".format(letters[next_col + 9], row), product.name, format6_l)
                worksheet.write(
                    "{}{}".format(letters[next_col + 10], row), product.create_date.strftime("%d-%m-%Y"), format6_l
                )
                worksheet.write("{}{}".format(letters[next_col + 11], row), product_tax_categories, format6_l)
                worksheet.write(
                    "{}{}".format(letters[next_col + 12], row), warehouse_id.name if warehouse_id else "", format6_l
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 13], row),
                    product.default_code if product.default_code else "",
                    format6_l,
                )
                worksheet.write("{}{}".format(letters[next_col + 14], row), supplier, format6_l)
                worksheet.write(
                    "{}{}".format(letters[next_col + 15], row),
                    product.supplier_sku_no if product.supplier_sku_no else "",
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 16], row),
                    product.product_breeder_id.breeder_name if product.product_breeder_id else "",
                    format6_l,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 17], row),
                    "Yes" if product.is_excluded_customer else "No",
                    format6_l,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 18], row),
                    product.case_quantity if product.case_quantity else "0",
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 19], row),
                    "Yes" if product.is_pending_discontinued else "No",
                    format6_l,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 20], row),
                    product.wholesale_price_value if product.wholesale_price_value else "0",
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 21], row),
                    product.retail_default_price if product.retail_default_price else "0",
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 22], row),
                    product.standard_price if product.standard_price else "0",
                    format6,
                )
                product_tag = ""
                for tag in product.product_tag_ids and product.product_tag_ids or "":
                    product_tag += str(tag.name) + ", "
                worksheet.write(
                    "{}{}".format(letters[next_col + 23], row),
                    product_tag,
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 24], row),
                    product.categ_id and product.categ_id.name or "",
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 25], row),
                    product.sudo().last_purchase_order_id and product.sudo().last_purchase_order_id.name or "",
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 26], row),
                    date_of_receipt.strftime("%d-%m-%Y") if date_of_receipt else "",
                    format6,
                )
                worksheet.write(
                    "{}{}".format(letters[next_col + 27], row), 0,format6)
                worksheet.write(
                    "{}{}".format(letters[next_col + 28], row),product_qty_delived if product_qty_delived else 0,format6) 
                worksheet.write(
                    "{}{}".format(letters[next_col + 29], row),order_qty_week if date_of_receipt else 0,format6)
                row += 1
