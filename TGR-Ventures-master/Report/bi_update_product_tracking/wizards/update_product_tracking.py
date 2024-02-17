from odoo import fields, models, _
from odoo.exceptions import UserError
import base64
import xlrd
import os


class UpdateProductTrackingWizard(models.TransientModel):
    _name = "update.tracking.wizard"
    _description = "Update Product Tracking Wizard"

    filename = fields.Char(string="File name")
    csv_file = fields.Binary("Upload File", attachment=True)

    def generate_update(self):
        if self.csv_file:
            file_value = self.csv_file.decode("utf-8")
            filename, FileExtension = os.path.splitext(self.filename)
            if FileExtension == ".csv":
                input_file = base64.b64decode(file_value)
                lst = []
                for loop in input_file.decode("utf-8"):
                    lst.append(loop)
                lsts = input_file.decode("utf-8").split("\n")
                lsts.pop(0)
                for rec in lsts:
                    if rec:
                        code = rec.split(",")
                        product_id = self.env["product.product"].search([("default_code", "=", code[0])])
                        if code[1] == 0:
                            product_id.write(
                                {
                                    "tracking": "none",
                                }
                            )
                        elif code[1] == 1:
                            product_id.write(
                                {
                                    "tracking": "lot",
                                }
                            )
            else:
                wb = xlrd.open_workbook(file_contents=base64.decodestring(self.csv_file))
                product_id_rno = 0
                tracking_rno = 1
                for sheet in wb.sheets():
                    for row in range(1, sheet.nrows):
                        barcode = str(sheet.cell(row, product_id_rno).value).split(".")[0]
                        product_id = self.env["product.product"].search([("default_code", "=", barcode)])
                        if not product_id:
                            raise UserError(_("Product not found at row %s" % (row + 1)))
                        tracking = sheet.cell(row, tracking_rno).value
                        if tracking == 0:
                            product_id.write(
                                {
                                    "tracking": "none",
                                }
                            )
                        elif tracking == 1:
                            product_id.write(
                                {
                                    "tracking": "lot",
                                }
                            )
