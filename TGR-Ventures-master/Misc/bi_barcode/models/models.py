from odoo import fields, models
import base64
import xlrd
import os


class BiBarCode(models.Model):
    _name = "bi.barcode"
    _description = "bi barcode"

    # @api.model
    # def create(self, vals):
    #     vals["name"] = self.env["ir.sequence"].next_by_code("barcode.print")
    #     result = super(BiBarCode, self).create(vals)
    #     return result

    name = fields.Char(placeholder="Name")
    barcode_line_ids = fields.One2many("bi.barcode.line", "barcode_print_id")

    filename = fields.Char(string="File name")
    csv_file = fields.Binary("Upload File", attachment=True)

    def generate_update(self):
        if self.csv_file:
            file_value = self.csv_file.decode("utf-8")
            filename, FileExtension = os.path.splitext(self.filename)
            if FileExtension == ".csv":
                data_list = []
                input_file = base64.b64decode(file_value)
                lst = []
                for loop in input_file.decode("utf-8"):
                    lst.append(loop)
                lsts = input_file.decode("utf-8").split("\n")
                lsts.pop(0)
                # print (sdf)
                for rec in lsts:
                    if rec:
                        code = rec.split(",")
                        product_id = self.env["product.product"].search([("barcode", "=", code[0])])
                        data_list.append(
                            (
                                0,
                                0,
                                {
                                    #  'product_id': code[0],
                                    "product_id": product_id.id,
                                    "quantity": code[1],
                                },
                            )
                        )
                self.barcode_line_ids = data_list
            else:
                wb = xlrd.open_workbook(file_contents=base64.decodestring(self.csv_file))
                product_id_rno = 0
                quantity_rno = 1
                data_list = []
                for sheet in wb.sheets():
                    for row in range(1, sheet.nrows):
                        product_id = self.env["product.product"].search(
                            [("default_code", "=", sheet.cell(row, product_id_rno).value)]
                        )
                        if product_id:
                            quantity = sheet.cell(row, quantity_rno).value
                            data_list.append(
                                (
                                    0,
                                    0,
                                    {
                                        "product_id": product_id.id,
                                        "quantity": quantity,
                                    },
                                )
                            )
                self.barcode_line_ids = data_list

    def print_barcode(self):
        return self.env.ref("bi_barcode.label_barcode_product_product_print").report_action(self, config=False)

    def print_usa_barcode(self):
        return self.env.ref("bi_barcode.usa_label_barcode_print").report_action(self, config=False)


class BiBarCodeLine(models.Model):
    _name = "bi.barcode.line"
    _description = "bi barcode line"

    barcode_print_id = fields.Many2one("bi.barcode")
    product_id = fields.Many2one("product.product", string="Product")
    quantity = fields.Integer(string="Quantity")
