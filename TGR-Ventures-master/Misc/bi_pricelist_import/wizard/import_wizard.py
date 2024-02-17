from odoo import _, fields, models
from odoo.exceptions import UserError
import xlrd
import base64
from datetime import datetime


class ImportPricelist(models.Model):
    _inherit = "product.pricelist"

    excel_file = fields.Binary(string="Excel File", attachment=True)

    def export_template(self):
        return self.env.ref("bi_pricelist_import.action_pricelist_export_template").report_action(self, config=False)

    def load_lines(self):
        for record in self:
            if record.excel_file:
                values = []
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(record.excel_file))
                for sheet in workbook.sheets():
                    product_col = 0
                    line_qty = 1
                    line_price = 2
                    line_start_date = 3
                    line_end_date = 4
                    for row in range(1, sheet.nrows):
                        try:
                            product_id = self.env["product.template"].search(
                                [("default_code", "=", sheet.cell(row, product_col).value)]
                            )
                            if not product_id:
                                raise UserError(_("Product not found at row %s" % (row + 1)))
                            if sheet.cell(row, line_qty).value:
                                product_qty = sheet.cell(row, line_qty).value
                            else:
                                product_qty = 0
                            if sheet.cell(row, line_price).value:
                                product_price = sheet.cell(row, line_price).value
                            else:
                                product_price = 0
                            if sheet.cell(row, line_start_date).value:
                                DATETIME_FORMAT = "%d/%m/%Y"
                                if isinstance(sheet.cell(row, line_start_date).value, float):
                                    seconds = (sheet.cell(row, line_start_date).value - 25569) * 86400.0
                                    product_start_date = datetime.utcfromtimestamp(seconds)
                                else:
                                    product_start_date = datetime.strptime(
                                        sheet.cell(row, line_start_date).value, DATETIME_FORMAT
                                    ).date()
                            else:
                                product_start_date = False
                            if sheet.cell(row, line_end_date).value:

                                DATETIME_FORMAT = "%d/%m/%Y"
                                if isinstance(sheet.cell(row, line_end_date).value, float):
                                    seconds = (sheet.cell(row, line_end_date).value - 25569) * 86400.0
                                    product_end_date = datetime.utcfromtimestamp(seconds)
                                else:
                                    product_end_date = datetime.strptime(
                                        sheet.cell(row, line_end_date).value, DATETIME_FORMAT
                                    ).date()
                            else:
                                product_end_date = False
                            values.append(
                                (
                                    0,
                                    0,
                                    {
                                        "product_tmpl_id": product_id.id,
                                        "min_quantity": product_qty,
                                        "fixed_price": product_price,
                                        "date_start": product_start_date,
                                        "date_end": product_end_date,
                                    },
                                )
                            )
                        except IndexError:
                            break
                        row += 1
                    values = {
                        "item_ids": values,
                    }
                    self.write(values)
            else:
                raise UserError(_("Please Select Excel File"))

    def unlink_lines(self):
        self.item_ids = False
