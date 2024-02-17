from odoo import models


class BiProductWiseReport(models.AbstractModel):
    _name = "report.x_product_move_report.product_activity_report_xl"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Product Activity Analysis")
        from_date = data["form"]["date_from"]
        to_date = data["form"]["date_to"]
        product_id = data["form"]["product_id"]
        location_id = data["form"]["location_id"]

        domain = [("state", "=", "done"), ("product_id", "=", product_id[0])]
        if from_date:
            domain.append(("date", ">=", from_date))
        if to_date:
            domain.append(("date", "<=", to_date))
        if location_id:
            domain.append("|")
            domain.append(("location_id", "=", location_id[0]))
            domain.append(("location_dest_id", "=", location_id[0]))

        move_line = self.env["stock.move.line"].search(domain, order="date ASC")

        table_head_format = workbook.add_format(
            {"align": "center", "border": 2, "valign": "vcenter", "bg_color": "#D6D6D6"}
        )
        table_data_format = workbook.add_format(
            {
                "font_size": 10,
                "align": "center",
                "valign": "vcenter",
                "border": 1,
            }
        )

        worksheet.merge_range("A1:F1", None, table_head_format)
        worksheet.set_row(0, 40)
        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:B", 28)
        worksheet.set_column("C:C", 20)
        worksheet.set_column("D:D", 20)
        worksheet.set_column("E:E", 25)
        worksheet.set_column("F:F", 25)

        # worksheet.write("A3", "Date", table_head_format)
        # worksheet.write('B3', "Transfer ID", table_head_format)
        # worksheet.write('C3', "Origin", table_head_format)
        # worksheet.write('D3', "Move Type", table_head_format)
        # worksheet.write('E3', "Qty Done", table_head_format)
        # worksheet.write('F3', "Qty On Hand", table_head_format)

        row = 2
        t_qty_done = 0
        move_type = {
            "incoming": "IN",
            "outgoing": "OUT",
            "internal": "INT",
        }

        if location_id:
            worksheet.merge_range(
                "A{}:F{}".format(row, row), "Location: {}".format(location_id[1] if location_id else ""), table_head_format
            )
            row += 1
            worksheet.write("A%s" % row, "Date", table_head_format)
            worksheet.write("B%s" % row, "Transfer ID", table_head_format)
            worksheet.write("C%s" % row, "Origin", table_head_format)
            worksheet.write("D%s" % row, "Move Type", table_head_format)
            worksheet.write("E%s" % row, "Qty Done", table_head_format)
            worksheet.write("F%s" % row, "Qty On Hand", table_head_format)
            row += 1
            for line in move_line:
                worksheet.write("A%s" % row, line.date.strftime("%d-%m-%Y"), table_data_format)
                worksheet.write("B%s" % row, line.reference if line.reference else "", table_data_format)
                worksheet.write("C%s" % row, line.origin if line.origin else "", table_data_format)
                worksheet.write("D%s" % row, move_type.get(line.picking_code), table_data_format)
                worksheet.write("E%s" % row, line.qty_done, table_data_format)

                if (
                    line.picking_code == "outgoing"
                    or line.location_dest_id.usage in ["inventory", "transit", "customer"]
                    or (location_id and line.location_id.id == location_id[0])
                ):
                    t_qty_done = t_qty_done - line.qty_done
                elif (
                    line.picking_code == "incoming"
                    or (
                        location_id
                        and line.location_dest_id.id == location_id[0]
                        and line.location_dest_id.usage == "internal"
                    )
                    or (line.location_dest_id.usage == "internal" and line.location_id.usage != "internal")
                ):
                    t_qty_done = t_qty_done + line.qty_done
                worksheet.write("F%s" % row, t_qty_done, table_data_format)
                row += 1

                worksheet.write(
                    "A1",
                    "Product Activity Analysis for: {}".format(product_id[1] if product_id else ""),
                    table_head_format,
                )
        else:
            from_location = move_line.mapped("location_id.id")
            to_location = move_line.mapped("location_dest_id.id")
            stock_location = (
                self.env["stock.location"]
                .search([("usage", "=", "internal")])
                .filtered(lambda location: location.id in from_location or location.id in to_location)
            )
            for location in stock_location:
                t_qty_done = 0
                worksheet.merge_range(
                    "A{}:F{}".format(row, row),
                    "Location: {}".format(location.display_name if location.display_name else ""),
                    table_head_format,
                )
                row += 1
                worksheet.write("A%s" % row, "Date", table_head_format)
                worksheet.write("B%s" % row, "Transfer ID", table_head_format)
                worksheet.write("C%s" % row, "Origin", table_head_format)
                worksheet.write("D%s" % row, "Move Type", table_head_format)
                worksheet.write("E%s" % row, "Qty Done", table_head_format)
                worksheet.write("F%s" % row, "Qty On Hand", table_head_format)
                row += 1

                for line in move_line.filtered(
                    lambda x: x.location_id.id == location.id or x.location_dest_id.id == location.id
                ):

                    worksheet.write("A%s" % row, line.date.strftime("%d-%m-%Y"), table_data_format)
                    worksheet.write("B%s" % row, line.reference if line.reference else "", table_data_format)
                    worksheet.write("C%s" % row, line.origin if line.origin else "", table_data_format)
                    worksheet.write("D%s" % row, move_type.get(line.picking_code), table_data_format)
                    worksheet.write("E%s" % row, line.qty_done, table_data_format)

                    if (
                        line.picking_code == "outgoing"
                        or line.location_dest_id.usage in ["inventory", "transit", "customer"]
                        or (location_id and line.location_id.id == location_id[0] or location.id == line.location_id.id)
                    ):
                        t_qty_done = t_qty_done - line.qty_done
                    elif (
                        line.picking_code == "incoming"
                        or (
                            location_id
                            and line.location_dest_id.id == location_id[0]
                            and line.location_dest_id.usage == "internal"
                        )
                        or (line.location_dest_id.usage == "internal" and line.location_id.usage != "internal")
                        or location.id == line.location_dest_id.id
                    ):
                        t_qty_done = t_qty_done + line.qty_done
                    worksheet.write("F%s" % row, t_qty_done, table_data_format)
                    row += 1

                    worksheet.write(
                        "A1",
                        "Product Activity Analysis for: {}".format(product_id[1] if product_id else ""),
                        table_head_format,
                    )
