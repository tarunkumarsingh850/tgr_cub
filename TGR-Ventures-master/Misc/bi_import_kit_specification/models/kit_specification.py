from odoo import _, fields, models
from odoo.exceptions import UserError
import xlrd
import base64


class ImportDAta(models.Model):
    _inherit = "bill.material"

    excel_file = fields.Binary(string="Excel File", attachment=True)

    def load_lines(self):
        for record in self:
            if record.excel_file:
                values = []
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(record.excel_file))
                for sheet in workbook.sheets():
                    kit_product_col = 0
                    line_qty = 1
                    for row in range(1, sheet.nrows):
                        try:
                            product_id = self.env["product.product"].search(
                                [("default_code", "=", sheet.cell(row, kit_product_col).value)]
                            )
                            if not product_id:
                                raise UserError(_("Product not found at row %s" % (row + 1)))

                            product_qty = sheet.cell(row, line_qty).value
                            values.append(
                                (
                                    0,
                                    0,
                                    {
                                        "product_id": product_id.id,
                                        "line_quantity": product_qty,
                                        "line_uom_id": product_id.uom_id.id,
                                        # "unit_cost": product_id.standard_price,
                                    },
                                )
                            )

                        except IndexError:
                            break
                        row += 1
                    values = {
                        "bom_line_ids": values,
                    }
                    self.write(values)
            else:
                raise UserError(_("Please Select Excel File"))
