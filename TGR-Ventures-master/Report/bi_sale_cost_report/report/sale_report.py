from odoo import api, models


class SaleWiseReportStructure(models.AbstractModel):
    _name = "report.bi_dynamic_sale_report.sale_order_report"
    _description = "Analysis Report PDF"

    @api.model
    def _get_report_values(self, docids, data=None):
        # If it is a call from Js window
        if self.env.context.get("from_js"):
            if data.get("js_data"):
                data.update(
                    {
                        "lines": data.get("js_data"),
                    }
                )
        return data

    @api.model
    def get_html(self, wizard):
        wizard_id = wizard
        obj = self.env["dynamic.sale.report"].search([("id", "=", wizard_id)])
        domain = []
        if obj.date_from:
            domain.append(("date_order", ">=", obj.date_from))
        if obj.date_to:
            domain.append(("date_order", "<=", obj.date_to))
        res = self._get_product_details(domain)
        res["lines"]["report_type"] = "html"
        res["lines"]["report_structure"] = "all"
        res["lines"]["date_from"] = obj.date_from.strftime("%d-%m-%Y")
        res["lines"]["date_to"] = obj.date_to.strftime("%d-%m-%Y")
        res["lines"] = self.env.ref("bi_dynamic_sale_report.dynamic_report_sale_wise")._render({"data": res["lines"]})
        return res

    def _get_product_details(self, domain, level=False):
        values = []
        lines = {}
        record = self.env["sale.order"].search(domain)
        for each in record:
            values.append(
                {
                    "type": each.order_type_id.name if each.order_type_id else "",
                    "ref": each.name,
                    "order_date": each.date_order,
                    "status": each.state.capitalize(),
                    "currency": each.currency_id.name if each.currency_id else "",
                    "cus_id": each.partner_id.customer_code,
                    "cus_name": each.partner_id.name,
                    "payment_method": each.payment_term_id.name if each.payment_term_id else "",
                    "warehouse": "",
                    "order_qty": 0,
                    "open_qty": 0,
                    "line_total": 0,
                    "open_amount": 0,
                }
            )
        lines = {
            "lines": sorted(values, key=lambda i: i["ref"], reverse=True),
        }
        return {"lines": lines}

    @api.model
    def get_report_datas(self, wizard, unfold=False):
        wizard_id = wizard
        obj = self.env["dynamic.sale.report"].search([("id", "=", wizard_id)])
        domain = []
        if obj.date_from:
            domain.append(("date_order", ">=", obj.date_from))
        if obj.date_to:
            domain.append(("date_order", "<=", obj.date_to))
        values = []
        lines = {}
        record = self.env["sale.order"].search(domain)
        for each in record:
            values.append(
                {
                    "type": each.order_type_id.name if each.order_type_id else "",
                    "ref": each.name,
                    "order_date": each.date_order,
                    "status": each.state.capitalize(),
                    "currency": each.currency_id.name if each.currency_id else "",
                    "cus_id": each.partner_id.customer_code,
                    "cus_name": each.partner_id.name,
                    "payment_method": each.payment_term_id.name if each.payment_term_id else "",
                    "warehouse": "",
                    "order_qty": 0,
                    "open_qty": 0,
                    "line_total": 0,
                    "open_amount": 0,
                }
            )
        lines = {
            "lines": sorted(values, key=lambda i: i["ref"], reverse=True),
        }
        return {"lines": lines}


class BiProductWiseReport(models.AbstractModel):
    _name = "report.bi_dynamic_sale_report.report_sale_dynamic"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Sale Report")
        justify = workbook.add_format({"bottom": True, "top": True, "right": True, "left": True, "font_size": 12})
        justify.set_align("justify")
        bolda = workbook.add_format({"bold": True, "align": "left"})
        boldc = workbook.add_format({"bold": True, "align": "center"})
        center = workbook.add_format({"align": "center"})
        worksheet.merge_range("A1:D1", "Product Wise Sales Report", bolda)

        worksheet.write("A3", "Company", bolda)
        worksheet.write("A4", "User", bolda)
        worksheet.merge_range("B3:D3", self.env.user.company_id.name, center)
        worksheet.merge_range("B4:D4", self.env.user.name, center)

        worksheet.write("F3", "Start Date", bolda)
        worksheet.write("F4", "End Date", bolda)
        worksheet.write("G3", data["form"]["date_from"], center)
        worksheet.write("G4", data["form"]["date_to"], center)

        row = 6
        new_row = row + 1
        worksheet.set_column("A:A", 10)
        worksheet.set_column("B:B", 15)
        worksheet.set_column("C:C", 15)
        worksheet.set_column("D:D", 15)
        worksheet.set_column("E:E", 15)
        worksheet.set_column("F:F", 15)
        worksheet.set_column("G:G", 25)
        worksheet.set_column("H:H", 18)
        worksheet.set_column("I:I", 15)
        worksheet.set_column("J:J", 15)
        worksheet.set_column("K:K", 15)
        worksheet.set_column("L:L", 15)
        worksheet.set_column("M:M", 15)

        worksheet.write("A%s" % row, "Type", boldc)
        worksheet.write("B%s" % row, "Ref.Nbr.", boldc)
        worksheet.write("C%s" % row, "Order Date", boldc)
        worksheet.write("D%s" % row, "Status Amount", boldc)
        worksheet.write("E%s" % row, "Currency", boldc)
        worksheet.write("F%s" % row, "Customer ID", boldc)
        worksheet.write("G%s" % row, "Customer Name", boldc)
        worksheet.write("H%s" % row, "Payment Method", boldc)
        worksheet.write("I%s" % row, "Warehouse", boldc)
        worksheet.write("J%s" % row, "Order Qty.", boldc)
        # worksheet.write("K%s" % row, "Open Qty.", boldc)
        worksheet.write("K%s" % row, "Line Total", boldc)
        # worksheet.write("L%s" % row, "Open Amount", boldc)
        worksheet.write("L%s" % row, "Logistics Costs", boldc)

        if not data.get("lines"):
            domain = []
            values = []
            if data["form"]["date_from"]:
                domain.append(("date_order", ">=", data["form"]["date_from"]))
            if data["form"]["date_to"]:
                domain.append(("date_order", "<=", data["form"]["date_to"]))
            # if data["form"]["partner_id"]:
            #     domain.append(("partner_id", "=",data["form"]["partner_id"]))
            record = self.env["sale.order"].search(domain)
            for each in record:
                qty = sum(
                    each.order_line.filtered(lambda m: m.product_id.detailed_type == "product").mapped("product_qty")
                )
                total = sum(each.order_line.mapped("price_subtotal"))
                values.append(
                    {
                        "type": each.order_type_id.name if each.order_type_id else "",
                        "ref": each.name,
                        "order_date": each.date_order,
                        "status": each.state.capitalize(),
                        "currency": each.currency_id.name if each.currency_id else "",
                        "cus_id": each.partner_id.customer_code,
                        "cus_name": each.partner_id.name,
                        "payment_method": each.payment_term_id.name if each.payment_term_id else "",
                        "warehouse": each.warehouse_id.name if each.warehouse_id else "",
                        "order_qty": qty if qty else "",
                        "line_total": total if total else "",
                        "logistics_costs": each.logistics_costs if each.logistics_costs else "",
                    }
                )

            for item in sorted(values, key=lambda i: i["ref"], reverse=True):
                worksheet.write("A%s" % new_row, item.get("type"), center)
                worksheet.write("B%s" % new_row, item.get("ref"), center)
                worksheet.write("C%s" % new_row, str(item.get("order_date")), center)
                worksheet.write("D%s" % new_row, item.get("status"), center)
                worksheet.write("E%s" % new_row, item.get("currency"), center)
                worksheet.write("F%s" % new_row, item.get("cus_id"), center)
                worksheet.write("G%s" % new_row, item.get("cus_name"), center)
                worksheet.write("H%s" % new_row, item.get("payment_method"), center)
                worksheet.write("I%s" % new_row, item.get("warehouse"), center)
                worksheet.write("J%s" % new_row, item.get("order_qty"), center)
                # worksheet.write("K%s" % new_row, item.get("open_qty"), center)
                worksheet.write("K%s" % new_row, item.get("line_total"), center)
                # worksheet.write("L%s" % new_row, item.get("open_amount"), center)
                worksheet.write("L%s" % new_row, item.get("logistics_costs"), center)
                new_row += 1
        else:
            for each in data["lines"]:
                worksheet.write("A%s" % new_row, each.get("type"), center)
                worksheet.write("B%s" % new_row, each.get("ref"), center)
                worksheet.write("C%s" % new_row, each.get("order_date"), center)
                worksheet.write("D%s" % new_row, each.get("status"), center)
                worksheet.write("E%s" % new_row, each.get("currency"), center)
                worksheet.write("F%s" % new_row, each.get("cus_id"), center)
                worksheet.write("G%s" % new_row, each.get("cus_name"), center)
                worksheet.write("H%s" % new_row, each.get("payment_method"), center)
                worksheet.write("I%s" % new_row, each.get("warehouse"), center)
                worksheet.write("J%s" % new_row, each.get("order_qty"), center)
                # worksheet.write("K%s" % new_row, each.get("open_qty"), center)
                worksheet.write("K%s" % new_row, each.get("line_total"), center)
                # worksheet.write("L%s" % new_row, each.get("open_amount"), center)
                new_row += 1
