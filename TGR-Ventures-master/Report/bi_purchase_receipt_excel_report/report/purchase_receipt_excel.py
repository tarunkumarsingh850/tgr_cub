import base64
import io
from PIL import Image
from odoo import models


class PurchaseReceiptReportxlsx(models.AbstractModel):
    _name = "report.bi_purchase_receipt_excel_report.purchase_receipt_rpt"
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
        sheet = workbook.add_worksheet("Purchase Receipt Report")
        row = 1

        merge_format = workbook.add_format({"align": "left", "text_wrap": True, "valign": "vcenter"})
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
        bound_width_height = (150, 180)

        if lines.company_id.logo:
            image_byte_stream = io.BytesIO(base64.b64decode(lines.company_id.logo))
            if image_byte_stream:
                image_data = self.get_resized_image_data(image_byte_stream, bound_width_height)
                if image_data:
                    sheet.insert_image(
                        "H1:H7", "Header Image", {"image_data": image_data, "x_offset": 11, "y_offset": 8}
                    )
        sheet.set_column("B:B", 25)
        sheet.set_column("C:C", 20)
        sheet.set_column("D:D", 20)
        sheet.set_column("E:E", 20)
        sheet.set_column("F:F", 20)
        sheet.set_column("G:G", 20)
        sheet.set_column("H:H", 20)
        sheet.merge_range("A1:E7", "", merge_format)
        sheet.merge_range("F9:H10", "Receipt", merge_format1)
        sheet.merge_range("A9:E9", "FROM :", merge_format3)
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

        sheet.write("A%s" % row, "\n".join(company_list), merge_format)
        sheet.merge_range(
            "F11:H17",
            f"{'Receipt Nbr:      ' + str(lines.name)}\n{'Date:      '+str(lines.scheduled_date)} \
                \n{'Vendor ID:      '+str(lines.partner_id.vendor_code)}",
            merge_format2,
        )
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

        sheet.merge_range("A10:E17", "\n".join(partner_list), merge_format)
        row = 19
        sheet.write("A%s" % row, "No", merge_format5)
        sheet.write("B%s" % row, "SKU", merge_format5)
        sheet.write("C%s" % row, "ITEM", merge_format5)
        sheet.write("D%s" % row, "PO ORDER", merge_format5)
        sheet.write("E%s" % row, "UOM", merge_format5)
        sheet.write("F%s" % row, "QTY", merge_format5)
        sheet.write("G%s" % row, "UNIT COST", merge_format5)
        sheet.write("H%s" % row, "EXT.COST", merge_format5)
        sheet.write("I%s" % row, "CURRENCY", merge_format5)
        row += 1
        sl_no = 1
        total_qty = 0
        receipt_total = 0
        for lines_rec in lines.move_ids_without_package:
            sheet.write("A%s" % row, sl_no, merge_format4)
            sl_no += 1
            sheet.write(
                "B%s" % row,
                lines_rec.product_id.default_code if lines_rec.product_id.default_code else "",
                merge_format4,
            )
            sheet.write("C%s" % row, lines_rec.product_id.name if lines_rec.product_id.name else "", merge_format)
            sheet.write("D%s" % row, lines.purchase_id.name if lines.purchase_id.name else "", merge_format)
            sheet.write("E%s" % row, lines_rec.product_uom.name if lines_rec.product_uom.name else "", merge_format6)
            sheet.write("F%s" % row, lines_rec.product_uom_qty if lines_rec.product_uom_qty else "", merge_format4)
            sheet.write("G%s" % row, lines_rec.price_unit if lines_rec.price_unit else "", merge_format4)
            sheet.write(
                "H%s" % row,
                lines_rec.purchase_line_id.price_subtotal if lines_rec.purchase_line_id.price_subtotal else "",
                merge_format4,
            )
            sheet.write(
                "I%s" % row,
                lines_rec.purchase_line_id.currency_id.name if lines_rec.purchase_line_id.currency_id.name else "",
                merge_format6,
            )
            total_qty += lines_rec.product_uom_qty
            receipt_total += lines_rec.purchase_line_id.price_subtotal
            row += 1
        sheet.merge_range("A{}:I{}".format(row, row), "", merge_format7)
        row += 1
        sheet.write("F%s" % row, "Total Qty", merge_format2)
        sheet.write("H%s" % row, total_qty, merge_format4)
        row += 1
        sheet.write("F%s" % row, "Receipt Total", merge_format2)
        sheet.write("H%s" % row, receipt_total, merge_format4)
