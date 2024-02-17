from odoo import fields, models, _
from odoo.exceptions import UserError
import base64
import xlrd
import os


class ShippingTrackingWizard(models.TransientModel):
    _name = "shipping.tracking.wizard"
    _description = "Update Shipment Tracking Wizard"

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
                        stock_id = self.env["stock.picking"].search([("name", "=", code[0])])
                        if code[2]:
                            stock_id.write(
                                {
                                    "carrier_tracking_ref": code[2],
                                }
                            )
            else:
                wb = xlrd.open_workbook(file_contents=base64.decodestring(self.csv_file))
                tracking_id = 0
                tracking_ref = 2
                for sheet in wb.sheets():
                    for row in range(1, sheet.nrows):
                        tracking_name = str(sheet.cell(row, tracking_id).value)
                        stock_id = self.env["stock.picking"].search([("name", "=", tracking_name)])
                        if not stock_id:
                            raise UserError(_("Tracking not found at row %s" % (row + 1)))
                        tracking = sheet.cell(row, tracking_ref).value
                        if tracking:
                            stock_id.write(
                                {
                                    "carrier_tracking_ref": tracking,
                                }
                            )
