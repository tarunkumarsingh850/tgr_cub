import base64
import io
from PIL import Image
from odoo import models


class InvoiceReportxlsx(models.AbstractModel):
    _name = "report.bi_invoice_excel_report.invoice_excel_rpt"
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
        sheet = workbook.add_worksheet("Invoice Excel Report")
        merge_format = workbook.add_format({"align": "left", "text_wrap": True, "valign": "vcenter"})
        merge_format1 = workbook.add_format({"fg_color": "#87ceeb"})
        merge_format2 = workbook.add_format(
            {"align": "left", "bold": True, "text_wrap": True, "valign": "vcenter", "fg_color": "#87ceeb"}
        )
        merge_format3 = workbook.add_format({"align": "left", "bold": True, "fg_color": "#87ceeb", "border": 1})
        merge_format4 = workbook.add_format({"align": "right", "border": 1})
        merge_format5 = workbook.add_format({"align": "left", "bold": True})
        merge_format6 = workbook.add_format({"align": "left", "border": 1, "text_wrap": True, "valign": "vcenter"})
        merge_format7 = workbook.add_format({"align": "right"})
        merge_format8 = workbook.add_format({"align": "left", "text_wrap": True, "valign": "vcenter", "border": 1})
        bound_width_height = (250, 150)

        if lines.company_id.logo:
            image_byte_stream = io.BytesIO(base64.b64decode(lines.company_id.logo))
            image_data = self.get_resized_image_data(image_byte_stream, bound_width_height)
        else:
            image_data = ""
        sheet.insert_image(
            "C2:D4", "Header Image", {"image_data": image_data if image_data else "", "x_offset": 11, "y_offset": 8}
        )
        sheet.set_column("A:A", 25)
        sheet.set_column("B:B", 20)
        sheet.set_column("C:C", 20)
        sheet.set_column("D:D", 20)
        sheet.set_column("E:E", 20)
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
        sheet.merge_range("A1:D7", "\n".join(company_list), merge_format)
        invoice_details = []
        if lines.name:
            invoice_details.append("Invoice No:      " + str(lines.name))
        if lines.invoice_date:
            invoice_details.append("Date:      " + str(lines.invoice_date))
        if lines.invoice_date_due:
            invoice_details.append("Due Date:      " + str(lines.invoice_date_due))
        if lines.partner_id.customer_code:
            invoice_details.append("Customer ID:      " + str(lines.partner_id.customer_code))
        if lines.currency_id.name:
            invoice_details.append("Currency:      " + str(lines.currency_id.name))
        sheet.merge_range("A11:D17", "", merge_format1)
        sheet.merge_range("E11:H17", "\n".join(invoice_details), merge_format2)
        sheet.merge_range("A19:C19", "BILL TO:", merge_format3)
        sheet.merge_range("D19:H19", "SHIP TO:", merge_format3)
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
        sheet.merge_range("A20:C27", "\n".join(partner_list), merge_format8)
        sheet.merge_range("D20:H27", "\n".join(partner_list), merge_format8)
        sheet.merge_range("A30:B30", "CUSTOMER REF.NUMBER ", merge_format3)
        sheet.merge_range("C30:E30", "TERMS", merge_format3)
        sheet.merge_range("F30:H30", "CONTACT", merge_format3)
        sheet.merge_range("A31:B31", lines.customer_order if lines.customer_order else "", merge_format6)
        sheet.merge_range("C31:E31", "", merge_format4)
        sheet.merge_range("F31:H31", "", merge_format4)
        row = 33
        sheet.write("A%s" % row, "SKU", merge_format3)
        sheet.write("B%s" % row, "Products", merge_format3)
        sheet.write("C%s" % row, "Pack Size", merge_format3)
        sheet.write("D%s" % row, "QTY", merge_format3)
        sheet.write("E%s" % row, "Price ", merge_format3)
        sheet.write("F%s" % row, "Discount", merge_format3)
        sheet.write("G%s" % row, "Disc.Price", merge_format3)
        sheet.write("H%s" % row, "Subtotal", merge_format3)
        row += 1
        total_net = 0
        total_discount = 0
        for lines_rec in lines.invoice_line_ids:
            sheet.write(
                "A%s" % row,
                lines_rec.product_id.default_code if lines_rec.product_id.default_code else "",
                merge_format6,
            )
            sheet.write("B%s" % row, lines_rec.product_id.name if lines_rec.product_id.name else "", merge_format6)
            sheet.write("C%s" % row, lines_rec.pack_size if lines_rec.pack_size else "", merge_format6)
            sheet.write("D%s" % row, lines_rec.quantity if lines_rec.quantity else "", merge_format4)
            sheet.write("E%s" % row, lines_rec.price_unit if lines_rec.price_unit else "", merge_format4)
            sheet.write("F%s" % row, lines_rec.discount_amount if lines_rec.discount_amount else "", merge_format4)
            sheet.write("G%s" % row, lines_rec.discount if lines_rec.discount else "", merge_format4)
            sheet.write("H%s" % row, lines_rec.price_subtotal if lines_rec.price_subtotal else "", merge_format4)
            total_net += lines_rec.price_subtotal
            total_discount += lines_rec.discount_amount
            row += 1
        row += 2
        sheet.merge_range("E{}:F{}".format(row, row), "Total Net:", merge_format5)
        sheet.write("H%s" % row, total_net, merge_format7)
        row += 1
        sheet.merge_range("E{}:F{}".format(row, row), "Total Discount:", merge_format5)
        sheet.write("H%s" % row, total_discount, merge_format7)
        row += 1
        sheet.merge_range("E{}:F{}".format(row, row), "Taxable amount: ", merge_format5)
        sheet.write("H%s" % row, "", merge_format7)
        row += 1
        sheet.merge_range("E{}:F{}".format(row, row), "Tax Total (0%): ", merge_format5)
        sheet.write("H%s" % row, lines.amount_tax, merge_format7)
        row += 1
        sheet.merge_range("E{}:F{}".format(row, row), "Grand Total:", merge_format5)
        sheet.write("H%s" % row, lines.amount_total, merge_format7)
