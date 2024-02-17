import base64
import io
from PIL import Image
from odoo import models


class InvoiceMemoReportxlsx(models.AbstractModel):
    _name = "report.bi_invoice_excel_report.invoice_memo_excel_rpt"
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
        merge_format = workbook.add_format({"align": "center", "text_wrap": True, "valign": "vcenter"})
        merge_format1 = workbook.add_format(
            {
                "bold": True,
                "font_color": "#808080",
            }
        )
        merge_format2 = workbook.add_format({"align": "left", "text_wrap": True, "valign": "vcenter", "border": 1})
        merge_format3 = workbook.add_format(
            {"align": "left", "text_wrap": True, "valign": "vcenter", "border": 1, "bold": True}
        )
        merge_format4 = workbook.add_format({"align": "left", "text_wrap": True, "font_size": 8, "valign": "vcenter"})

        sheet.set_column("A:A", 25)
        sheet.set_column("B:B", 25)
        sheet.set_column("C:C", 10)
        sheet.set_column("D:D", 10)
        sheet.set_column("E:E", 10)
        sheet.set_column("F:F", 20)
        sheet.set_column("G:G", 10)
        sheet.set_column("H:H", 10)
        sheet.set_row(2, 10)
        sheet.set_row(3, 10)
        sheet.set_row(4, 10)
        sheet.set_row(5, 10)
        sheet.set_row(6, 10)
        sheet.set_row(7, 10)
        sheet.set_row(8, 10)
        bound_width_height = (150, 200)

        sheet.merge_range("A1:H1", "Invoice/Memo", merge_format)
        if lines.company_id.logo:
            image_byte_stream = io.BytesIO(base64.b64decode(lines.company_id.logo))
            image_data = self.get_resized_image_data(image_byte_stream, bound_width_height)
            sheet.insert_image("A3:A7", "Header Image", {"image_data": image_data, "x_offset": 20, "y_offset": -1})
        sheet.write("B3", lines.company_id.name if lines.company_id.name else "", merge_format4)
        sheet.write("B4", lines.company_id.street if lines.company_id.street else "", merge_format4)
        sheet.write("B5", lines.company_id.street2 if lines.company_id.street2 else "", merge_format4)
        sheet.write("B6", f"Phone:{lines.company_id.phone}" if lines.company_id.phone else "Phone:", merge_format4)
        sheet.write(
            "B7", f"VAT Number:{lines.company_id.vat}" if lines.company_id.vat else "VAT Number:", merge_format4
        )
        sheet.write("F3", "Account Holder:", merge_format4)
        sheet.write("F4", "Bank Name:", merge_format4)
        sheet.write("F5", "Bank Address:", merge_format4)
        sheet.write("F6", "IBAN:", merge_format4)
        sheet.write("F7", "BIC:", merge_format4)
        sheet.write("F8", "Currency:", merge_format4)

        sheet.write("A11", "Invoice No.:", merge_format1)
        sheet.merge_range("B11:C11", lines.name if lines.name else "", merge_format1)
        sheet.write("D11", "SOBatch Nbr:", merge_format1)
        sheet.write("E11", "", merge_format1)
        sheet.write("F11", "VAT Number:", merge_format1)
        sheet.merge_range("G11:H11", lines.partner_id.vat if lines.partner_id.vat else "", merge_format1)
        sheet.write("A12", "Dispatch Date:", merge_format1)
        sheet.merge_range("B12:C12", "", merge_format1)
        sheet.write("F12", "Invoice Date:", merge_format1)
        sheet.merge_range("G12:H12", lines.invoice_date if lines.invoice_date else "", merge_format1)
        sheet.write("F13", "Currency:", merge_format1)
        sheet.merge_range("G13:H13", lines.currency_id.name if lines.currency_id.name else "", merge_format1)

        sheet.merge_range("A15:C15", "SOLD TO:", merge_format3)
        sheet.merge_range("D15:H15", "DELIVER TO:", merge_format3)
        sheet.merge_range("A16:C16", lines.partner_id.street, merge_format2)
        sheet.merge_range("D16:H16", lines.partner_id.street, merge_format2)
        sheet.merge_range("A17:C17", f"{lines.partner_id.street}{lines.partner_id.city}", merge_format2)
        sheet.merge_range("D17:H17", f"{lines.partner_id.street}{lines.partner_id.city}", merge_format2)
        sheet.merge_range("A18:C18", f"{lines.partner_id.state_id.name}{lines.partner_id.zip}", merge_format2)
        sheet.merge_range("D18:H18", f"{lines.partner_id.state_id.name}{lines.partner_id.zip}", merge_format2)
        sheet.merge_range("A19:C19", lines.partner_id.country_id.name, merge_format2)
        sheet.merge_range("D19:H19", lines.partner_id.country_id.name, merge_format2)

        sheet.merge_range("A21:C21", "ORDER #", merge_format3)
        sheet.merge_range("D21:E21", "TERMS", merge_format3)
        sheet.merge_range("F21:H21", "CONTACT", merge_format3)
        sheet.merge_range("A22:C22", lines.invoice_origin if lines.invoice_origin else "", merge_format2)
        sheet.merge_range(
            "D22:E22", lines.invoice_payment_term_id.name if lines.invoice_payment_term_id.name else "", merge_format2
        )
        sheet.merge_range("F22:H22", "", merge_format2)

        sheet.merge_range("A24:C24", "Payment Method", merge_format3)
        sheet.merge_range("D24:H24", "Delivery Method", merge_format3)
        sheet.merge_range("A25:C25", "", merge_format2)
        sheet.merge_range("D25:H25", "", merge_format2)

        sheet.write("A27", "SKU", merge_format3)
        sheet.write("B27", "Products", merge_format3)
        sheet.write("C27", "Pack Size", merge_format3)
        sheet.write("D27", "QTY", merge_format3)
        sheet.write("E27", "Price", merge_format3)
        sheet.write("F27", "Discount", merge_format3)
        sheet.write("G27", "Disc.Price", merge_format3)
        sheet.write("H27", "Subtotal", merge_format3)

        discount = 0
        total_discount = 0
        amount = 0
        row = 28
        for line in lines.invoice_line_ids:
            sheet.write(
                "A%s" % row,
                line.product_id.product_tmpl_id.default_code if line.product_id.product_tmpl_id.default_code else "",
                merge_format2,
            )
            sheet.write(
                "B%s" % row,
                line.product_id.product_tmpl_id.name if line.product_id.product_tmpl_id.name else "",
                merge_format2,
            )
            sheet.write(
                "C%s" % row,
                line.product_id.product_tmpl_id.pack_size_desc
                if line.product_id.product_tmpl_id.pack_size_desc
                else "",
                merge_format2,
            )
            sheet.write("D%s" % row, line.quantity if line.quantity else "", merge_format2)
            sheet.write("E%s" % row, line.price_unit if line.price_unit else "", merge_format2)
            sheet.write("F%s" % row, line.discount if line.discount else "", merge_format2)
            discount = (line.quantity * line.price_unit) * line.discount / 100
            sheet.write("G%s" % row, discount if discount else "", merge_format2)
            sheet.write("H%s" % row, line.price_subtotal if line.price_subtotal else "", merge_format2)
            total_discount += (line.quantity * line.price_unit) * line.discount / 100
            amount += line.quantity * line.price_unit
            row += 1
        row += 1
        sheet.merge_range(row, 5, row, 6, "Total Net:", merge_format3)
        row += 1
        sheet.write("H%s" % row, "%.2f" % amount if amount else "", merge_format2)

        sheet.merge_range(row, 5, row, 6, "Total Discount:", merge_format3)
        row += 1
        sheet.write("H%s" % row, "%.2f" % total_discount if total_discount else "", merge_format2)
        # row +=1
        sheet.merge_range(row, 5, row, 6, "Taxable amount:", merge_format3)
        row += 1
        sheet.write("H%s" % row, "%.2f" % lines.amount_untaxed if lines.amount_untaxed else "", merge_format2)
        # row +=1
        sheet.merge_range(row, 5, row, 6, "Tax Total:", merge_format3)
        row += 1
        sheet.write("H%s" % row, "%.2f" % lines.amount_tax if lines.amount_tax else "", merge_format2)
        # row +=1
        sheet.merge_range(row, 5, row, 6, "Grand Total:", merge_format3)
        row += 1
        sheet.write("H%s" % row, "%.2f" % lines.amount_total if lines.amount_total else "", merge_format2)
