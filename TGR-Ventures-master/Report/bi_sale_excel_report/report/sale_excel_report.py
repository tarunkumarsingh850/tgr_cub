import base64
import io
from PIL import Image
from odoo import models


class PurchaseOrderReportxlsx(models.AbstractModel):
    _name = "report.bi_sale_excel_report.sale_order_rpt"
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
        sheet = workbook.add_worksheet("Sale Order Report")
        merge_format = workbook.add_format({"align": "left", "text_wrap": True, "valign": "vcenter"})
        merge_format2 = workbook.add_format({"align": "left", "bold": True, "text_wrap": True, "valign": "vcenter"})
        merge_format3 = workbook.add_format(
            {"align": "left", "bold": True, "fg_color": "#00008B", "color": "#FFFFFF", "border": 1}
        )
        merge_format4 = workbook.add_format({"align": "right", "border": 1})
        merge_format5 = workbook.add_format({"top": True, "border_color": "blue", "align": "left", "bold": True})
        merge_format6 = workbook.add_format({"align": "center", "border": 1})
        merge_format7 = workbook.add_format({"left": True, "border_color": "blue"})
        merge_format8 = workbook.add_format(
            {"align": "center", "bold": True, "fg_color": "#00008B", "font_size": 28, "color": "#FFFFFF"}
        )
        merge_format9 = workbook.add_format({"align": "left", "text_wrap": True, "valign": "vcenter", "border": 1})
        merge_format10 = workbook.add_format(
            {"align": "left", "bold": True, "fg_color": "#00008B", "color": "#FFFFFF", "border": 1}
        )
        merge_format11 = workbook.add_format({"left": True, "border_color": "blue", "bottom": True})
        merge_format12 = workbook.add_format({"border_color": "blue", "bottom": True})
        merge_format13 = workbook.add_format({"left": True, "border_color": "blue", "top": True})
        merge_format14 = workbook.add_format({"border_color": "blue", "top": True, "bold": True})
        merge_format15 = workbook.add_format({"border_color": "blue", "top": True, "right": True})
        merge_format16 = workbook.add_format({"border_color": "blue", "right": True})
        merge_format17 = workbook.add_format({"border_color": "blue", "right": True, "bottom": True})
        merge_format18 = workbook.add_format({"align": "left", "bold": True, "bottom": True})
        merge_format19 = workbook.add_format(
            {"align": "center", "bold": True, "fg_color": "#00008B", "color": "#FFFFFF", "border": 1}
        )
        bound_width_height = (150, 280)
        if lines.company_id.logo:
            image_byte_stream = io.BytesIO(base64.b64decode(lines.company_id.logo))
            image_data = self.get_resized_image_data(image_byte_stream, bound_width_height)
            sheet.insert_image("F1:H7", "Header Image", {"image_data": image_data, "x_offset": 11, "y_offset": 8})
        sheet.set_column("B:B", 20)
        sheet.set_column("C:C", 20)
        sheet.set_column("D:D", 20)
        sheet.set_column("E:E", 20)
        sheet.set_column("H:H", 20)
        sheet.set_column("I:I", 20)
        sheet.set_column("G:G", 20)
        sheet.merge_range("E9:I10", "Sales Order", merge_format8)
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
        row = 1
        sheet.merge_range("A1:D7", "\n".join(company_list), merge_format)
        sale_order_details = []
        if lines.name:
            sale_order_details.append("Order No:      " + str(lines.name))
        if lines.date_order:
            sale_order_details.append("Order Date:       " + str(lines.date_order))
        if lines.picking_ids.scheduled_date:
            sale_order_details.append("Delivery Date:     " + str(lines.picking_ids.scheduled_date))
        if lines.partner_id.customer_code:
            sale_order_details.append("Customer ID:      " + str(lines.partner_id.vendor_code))
        if lines.currency_id.name:
            sale_order_details.append("Currency:       " + str(lines.currency_id.name))
        sheet.merge_range("E11:I17", "\n".join(sale_order_details), merge_format2)
        sheet.merge_range("A19:C19", "BILL TO:", merge_format3)
        sheet.merge_range("D19:I19", "SHIP TO:", merge_format3)
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
        sheet.merge_range("A20:C27", "\n".join(partner_list), merge_format9)
        sheet.merge_range("D20:I27", "\n".join(partner_list), merge_format9)
        sheet.merge_range("A28:B28", "CUSTOMER P.O. NO.", merge_format10)
        sheet.merge_range("C28:D28", "TERMS ", merge_format10)
        sheet.merge_range("E28:I28", "CONTACT ", merge_format10)
        sheet.merge_range("A29:B29", "", merge_format9)
        sheet.merge_range("C29:D29", "", merge_format9)
        sheet.merge_range("E29:I29", "", merge_format9)
        sheet.merge_range("A30:B30", "FOB POINT", merge_format10)
        sheet.merge_range("C30:D30", "SHIPPING TERMS", merge_format10)
        sheet.merge_range("E30:I30", "SHIP VIA", merge_format10)
        sheet.merge_range("A31:B31", "", merge_format9)
        sheet.merge_range("C31:D31", "", merge_format9)
        sheet.merge_range("E31:I31", "", merge_format9)
        row = 32
        sheet.write("A%s" % row, "NO.", merge_format19)
        sheet.write("B%s" % row, "SKU", merge_format19)
        sheet.merge_range("C{}:D{}".format(row, row), "ITEM ", merge_format19)
        sheet.write("E%s" % row, "QTY", merge_format19)
        sheet.write("F%s" % row, "UOM", merge_format19)
        sheet.write("G%s" % row, "Price", merge_format19)
        sheet.write("H%s" % row, "Discount", merge_format19)
        sheet.write("I%s" % row, "EXTENDED PRICE", merge_format19)
        row += 1
        sl_no = 1
        unit_total = 0
        total_unit_total = 0
        discount_amount = 0
        for lines_rec in lines.order_line:
            sheet.write("A%s" % row, sl_no, merge_format4)
            sl_no += 1
            sheet.write("B%s" % row, lines_rec.product_id.default_code, merge_format9)
            sheet.merge_range("C{}:D{}".format(row, row), lines_rec.product_id.name, merge_format9)
            sheet.write("E%s" % row, lines_rec.product_uom_qty if lines_rec.product_uom_qty else "", merge_format4)
            sheet.write("F%s" % row, lines_rec.product_uom.name if lines_rec.product_uom.name else "", merge_format6)
            sheet.write("G%s" % row, lines_rec.price_unit if lines_rec.price_unit else "", merge_format4)
            sheet.write("H%s" % row, lines_rec.discount if lines_rec.discount else "", merge_format4)
            sheet.write("I%s" % row, lines_rec.price_subtotal if lines_rec.price_subtotal else "", merge_format4)
            unit_total = lines_rec.price_unit * lines_rec.product_uom_qty
            total_unit_total += unit_total
            row += 1
        row += 5
        sheet.write("A%s" % row, "", merge_format13)
        sheet.write("B%s" % row, "", merge_format5)
        sheet.write("C%s" % row, "", merge_format5)
        sheet.write("D%s" % row, "", merge_format5)
        sheet.write("E%s" % row, "Total Weight (EA): ", merge_format5)
        sheet.write("F%s" % row, "", merge_format5)
        sheet.write("G%s" % row, "", merge_format5)
        sheet.write("H%s" % row, "Sales Total: ", merge_format14)
        sheet.write("I%s" % row, total_unit_total, merge_format15)
        row += 1
        sheet.write("A%s" % row, "", merge_format7)
        sheet.write("B%s" % row, "", merge_format5)
        sheet.write("E%s" % row, "Total Volume (EA):", merge_format2)
        sheet.write("F%s" % row, "", merge_format)
        sheet.write("H%s" % row, "Freight & Misc.:", merge_format2)
        sheet.write("I%s" % row, "", merge_format16)
        row += 1
        sheet.write("A%s" % row, "", merge_format7)
        sheet.write("H%s" % row, "Less Discount: ", merge_format2)
        discount_amount = total_unit_total - lines.amount_untaxed
        sheet.write("I%s" % row, discount_amount, merge_format16)
        row += 1
        sheet.write("A%s" % row, "", merge_format7)
        sheet.write("H%s" % row, "Tax Total (0%): ", merge_format2)
        sheet.write("I%s" % row, lines.amount_tax, merge_format16)
        row += 1
        sheet.write("A%s" % row, "", merge_format11)
        sheet.write("B%s" % row, "", merge_format12)
        sheet.write("C%s" % row, "", merge_format12)
        sheet.write("D%s" % row, "", merge_format12)
        sheet.write("E%s" % row, "", merge_format12)
        sheet.write("F%s" % row, "", merge_format12)
        sheet.write("G%s" % row, "", merge_format12)
        sheet.write("H%s" % row, "Total (EUR):  ", merge_format18)
        sheet.write("I%s" % row, lines.amount_total, merge_format17)
