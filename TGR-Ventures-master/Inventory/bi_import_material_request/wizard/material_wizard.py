from odoo import _, fields, models
from odoo.exceptions import UserError
import xlrd
import base64


class MaterialWizard(models.TransientModel):
    _name = "material.request.wizard"
    _description = "Model is used to update lines"

    material_update_id = fields.Many2one("material.request")
    excel_file = fields.Binary(string="Excel File", attachment=True)

    def load_lines(self):
        for record in self:
            if record.excel_file:
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(record.excel_file))
                for sheet in workbook.sheets():
                    product_col = 0
                    qty_col = 1
                    values = []
                    for row in range(1, sheet.nrows):
                        try:
                            product_id = self.env["product.product"].search(
                                [("default_code", "=", sheet.cell(row, product_col).value)]
                            )
                            if not product_id:
                                raise UserError(_("Product not found at row %s" % (row + 1)))
                            product_qty = False
                            product_qty = sheet.cell(row, qty_col).value
                            values.append(
                                (
                                    0,
                                    0,
                                    {
                                        "product_id": product_id.id,
                                        "unit_of_measure": product_id.uom_id.id,
                                        "quantity": product_qty,
                                    },
                                )
                            )
                        except IndexError:
                            break
                    record.material_update_id.material_line_ids = False
                    record.material_update_id.material_line_ids = values
                    break
