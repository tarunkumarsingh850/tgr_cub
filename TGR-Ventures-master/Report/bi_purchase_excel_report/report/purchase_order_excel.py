import base64
import io
from PIL import Image
from odoo import models


class PurchaseOrderReportxlsx(models.AbstractModel):
    _name = "report.bi_purchase_excel_report.purchase_order_rpt"
    _inherit = "report.report_xlsx.abstract"

    def get_resized_image_data(self, byte_stream, bound_width_height):
        # get the byte stream of image and resize it
        im = Image.open(byte_stream)
        im.thumbnail(bound_width_height, Image.ANTIALIAS)
        # ANTIALIAS is important if shrinking
        # stuff the image data into a bytestream that excel can read
        im_bytes = io.BytesIO()
        im.save(im_bytes, format="PNG")
        return im_bytes

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet("Purchase Order Report")
        merge_format = workbook.add_format({"align": "left", "valign": "vcenter"})
        merge_format1 = workbook.add_format({"align": "left", "bold": True, "font_size": 28})
        merge_format2 = workbook.add_format({"align": "left", "bold": True, "text_wrap": True, "valign": "vcenter"})
        merge_format3 = workbook.add_format({"align": "left", "bold": True, "fg_color": "#D6EEEE"})
        merge_format4 = workbook.add_format(
            {
                "align": "right",
            }
        )
        merge_format5 = workbook.add_format({"align": "center", "bold": True, "fg_color": "#D6EEEE"})
        merge_format6 = workbook.add_format(
            {
                "align": "center",
            }
        )
        merge_format7 = workbook.add_format(
            {
                "top": True,
            }
        )
        bound_width_height = (220, 250)
        if lines.company_id.logo:
            image_byte_stream = io.BytesIO(base64.b64decode(lines.company_id.logo))
            image_data = self.get_resized_image_data(image_byte_stream, bound_width_height)
            sheet.insert_image("F1:H7", "Header Image", {"image_data": image_data, "x_offset": 11, "y_offset": 8})
        sheet.set_column("A:A", 25)
        sheet.set_column("B:B", 20)
        sheet.set_column("C:C", 20)
        sheet.set_column("D:D", 20)
        sheet.set_column("E:E", 15)
        sheet.merge_range("E9:L10", "Purchase Order", merge_format1)
        partner_list = []
        company_list = []
        if lines.company_id.name:
            company_list.append(lines.company_id.name)
        if lines.company_id.street:
            company_list.append(lines.company_id.street)
        if lines.company_id.street2:
            company_list.append(lines.company_id.street2)
        if lines.company_id.city:
            company_list.append(lines.company_id.city)
        if lines.company_id.state_id.name:
            company_list.append(lines.company_id.state_id.name)
        if lines.company_id.zip:
            company_list.append(lines.company_id.zip)
        if lines.company_id.country_id.name:
            company_list.append(lines.company_id.country_id.name)
        if lines.company_id.phone:
            company_list.append(lines.company_id.phone)
        ship_to = []
        ship_to.append("Tigre Uno Distribución S.L. ")
        ship_to.append("Pol. Ind. Guadalhorce")
        ship_to.append("C/ Diderot 66" + " " + "29004 MÁLAGA")
        ship_to.append("Spain")
        row = 1
        sheet.merge_range("A1:D7", "\n".join(company_list), merge_format)
        if lines.date_approve:
            data_to_approve = lines.date_approve
        else:
            data_to_approve = ""
        sheet.merge_range(
            "E11:L17",
            f"{'Currency:      ' + str(lines.currency_id.name)}\n{'Order No.      '+str(lines.name)} \
                \n{'Date:      '+str(data_to_approve)}\n{'Vendor ID:      '+str(lines.partner_id.vendor_code)}",
            merge_format2,
        )
        sheet.merge_range("A19:D19", "TO:", merge_format3)
        sheet.merge_range("E19:L19", "SHIP TO:", merge_format3)
        if lines.partner_id.name:
            partner_list.append(lines.partner_id.name)
        if lines.partner_id.street:
            partner_list.append(lines.partner_id.street)
        if lines.partner_id.street2:
            partner_list.append(lines.partner_id.street2)
        if lines.partner_id.city:
            partner_list.append(lines.partner_id.city)
        if lines.partner_id.state_id.name:
            partner_list.append(lines.partner_id.state_id.name)
        if lines.partner_id.zip:
            partner_list.append(lines.partner_id.zip)
        if lines.partner_id.country_id.name:
            partner_list.append(lines.partner_id.country_id.name)
        if lines.partner_id.phone:
            partner_list.append(lines.partner_id.phone)
        sheet.merge_range("A20:D27", "\n".join(partner_list), merge_format)
        sheet.merge_range("E20:L27", "\n".join(ship_to), merge_format)
        sheet.merge_range("A28:B28", "FOB POINT", merge_format3)
        sheet.merge_range("C28:D28", "SHIP VIA ", merge_format3)
        sheet.merge_range("E28:G28", "TERMS ", merge_format3)
        sheet.merge_range("H28:L28", "ORDER DATE ", merge_format3)
        if lines.date_approve:
            sheet.merge_range("I29:L29", lines.date_approve.strftime("%d/%m/%Y"), merge_format)
        row = 31
        sheet.write("A%s" % row, "Product SKU", merge_format5)
        sheet.write("B%s" % row, "Supplier SKU", merge_format5)
        sheet.merge_range("C{}:D{}".format(row, row), "ITEM", merge_format5)
        sheet.write("E%s" % row, "UOM", merge_format5)
        sheet.write("F%s" % row, "QTY", merge_format5)
        sheet.merge_range("G{}:H{}".format(row, row), "UNIT PRICE", merge_format5)
        sheet.merge_range("I{}:J{}".format(row, row), "EXTENDED PRICE", merge_format5)
        sheet.merge_range("K{}:L{}".format(row, row), "Warehouse", merge_format5)
        row += 1
        unit_price = 0
        total = 0

        for lines_rec in lines.order_line:
            sheet.write(
                "A%s" % row,
                lines_rec.product_id.default_code if lines_rec.product_id.default_code else "",
                merge_format6,
            )
            sheet.write(
                "B%s" % row,
                lines_rec.product_id.supplier_sku_no if lines_rec.product_id.supplier_sku_no else "",
                merge_format6,
            )
            sheet.merge_range("C{}:D{}".format(row, row), lines_rec.name if lines_rec.name else "", merge_format)
            sheet.write("E%s" % row, lines_rec.product_uom.name if lines_rec.product_uom.name else "", merge_format6)
            sheet.write("F%s" % row, lines_rec.product_qty if lines_rec.product_qty else "", merge_format4)
            sheet.merge_range(
                "G{}:H{}".format(row, row), lines_rec.price_unit if lines_rec.price_unit else "", merge_format4
            )
            sheet.merge_range(
                "I{}:J{}".format(row, row), lines_rec.price_subtotal if lines_rec.price_subtotal else "", merge_format4
            )
            sheet.merge_range(
                "K{}:L{}".format(row, row),
                lines_rec.warehouse_dest_id.name if lines_rec.warehouse_dest_id.name else "",
                merge_format6,
            )
            unit_price += lines_rec.price_unit
            total += lines_rec.price_subtotal
            row += 1
        sheet.merge_range("A{}:J{}".format(row, row), "", merge_format7)
        row += 1
        sheet.write("A%s" % row, "WAREHOUSE", merge_format2)
        warehouse = ""
        if lines[0].picking_ids and lines[0].picking_ids[0].location_dest_id.warehouse_id:
            warehouse = lines[0].picking_ids[0].location_dest_id.warehouse_id.name
        sheet.write("B%s" % row, warehouse, merge_format4)
        sheet.merge_range("G{}:H{}".format(row, row), "UNIT PRICE", merge_format2)
        sheet.write("J%s" % row, f"{unit_price}{lines.currency_id.symbol}", merge_format4)
        row += 1
        sheet.merge_range("G{}:H{}".format(row, row), "Tax Total: ", merge_format2)
        sheet.write("J%s" % row, f"{lines.amount_tax}{lines.currency_id.symbol}", merge_format4)
        row += 1
        sheet.merge_range("G{}:H{}".format(row, row), "Total (EUR): ", merge_format2)
        sheet.write("J%s" % row, f"{total}{lines.currency_id.symbol}", merge_format4)
