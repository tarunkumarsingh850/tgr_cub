from odoo import _, fields, models
from odoo.exceptions import UserError
import xlrd
import base64


class ExportWizard(models.TransientModel):
    _name = "export.wizard"
    _description = "Model is used to export"

    excel_file = fields.Binary(string="Excel File", attachment=True)
    product_ids = fields.Many2many("product.product", string="Product")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")

    def export_product_report(self):
        self.load_lines()

        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "product": self.product_ids.ids,
                "warehouse_id": self.warehouse_id.id,
            },
        }
        return self.env.ref("bi_product_report.action_export_report").report_action(self, data, config=False)

    def load_lines(self):
        for record in self:
            if record.excel_file:
                product_list = []
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(record.excel_file))
                for sheet in workbook.sheets():
                    product_col = 0
                    for row in range(1, sheet.nrows):
                        try:
                            product_id = self.env["product.product"].search(
                                [("default_code", "=", sheet.cell(row, product_col).value)]
                            )
                            if not product_id:
                                raise UserError(_("Product not found at row %s" % (row + 1)))
                            else:
                                for product in product_id:
                                    product_list.append(product.id)
                        except IndexError:
                            break
                        row += 1
                    break
                record.product_ids = [(6, 0, product_list)]

            else:
                raise UserError(_("Please Select Excel File"))
