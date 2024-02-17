from odoo import _, fields, models
from odoo.exceptions import UserError
import xlrd
import base64


class ImportLineKit(models.TransientModel):
    _name = "bill.material.wizard"

    excel_file = fields.Binary(string="Excel File", attachment=True)

    def export_template_kit(self):
        return self.env.ref("bi_kit_specification_import.action_export_template").report_action(self, config=False)

    def import_xls(self):
        for record in self:
            if record.excel_file:
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(record.excel_file))
                for sheet in workbook.sheets():
                    product_sku = 0
                    line_sku = 1
                    order = []
                    for row in range(1, sheet.nrows):
                        if sheet.cell(row, product_sku).value not in order:
                            order.append(sheet.cell(row, product_sku).value)
                    for each in order:
                        lines = []
                        for row in range(1, sheet.nrows):
                            if each == sheet.cell(row, product_sku).value:
                                product_id = self.env["product.product"].search(
                                    [("default_code", "=", sheet.cell(row, product_sku).value)], limit=1
                                )
                                if not product_id:
                                    raise UserError(_("Product not found at row %s" % (row + 1)))
                                product_line_id = self.env["product.product"].search(
                                    [("default_code", "=", sheet.cell(row, line_sku).value)], limit=1
                                )
                                if not product_line_id:
                                    raise UserError(_("Product not found at row %s" % (row + 1)))
                                lines.append(
                                    (
                                        0,
                                        0,
                                        {
                                            "product_id": product_line_id.id,
                                            "line_quantity": 1,
                                        },
                                    )
                                )
                        product_id = self.env["product.product"].search([("default_code", "=", each)], limit=1)
                        values = {
                            "product_id": product_id.id,
                            "quantity": 1,
                            "bom_line_ids": lines,
                        }
                        self.env["bill.material"].create(values)
                        # self.excel_file = False
            else:
                raise UserError(_("Please Select Excel File"))
