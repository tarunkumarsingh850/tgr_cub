from odoo import _, fields, models
from odoo.exceptions import UserError
import xlrd
import base64


class StockAdjustWizard(models.TransientModel):
    _name = "stock.adjustment.wizard"

    excel_file = fields.Binary(string="Excel File", attachment=True)

    def export_adj_template(self):
        return self.env.ref("bi_inv_adjustment_import.action_export_adj_template").report_action(self, config=False)

    def load_lines(self):
        count = 0
        for record in self:
            if record.excel_file:
                values = []
                stock_adj = self.env["stock.quant"]
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(record.excel_file))
                for sheet in workbook.sheets():
                    warehouse_col = 0
                    product_col = 1
                    qty_col = 2
                    for row in range(1, sheet.nrows):
                        try:
                            warehouse_id = self.env["stock.warehouse"].search(
                                [("name", "=", sheet.cell(row, warehouse_col).value)]
                            )
                            if not warehouse_id:
                                raise UserError(_("Loaction not found at row %s" % (row + 1)))

                            location = warehouse_id.lot_stock_id.id
                            product_id = self.env["product.product"].search(
                                [("default_code", "=", sheet.cell(row, product_col).value)]
                            )
                            if not product_id:
                                raise UserError(_("Product not found at row %s" % (row + 1)))
                            product = product_id.id

                            qty = sheet.cell(row, qty_col).value

                        except IndexError:
                            break
                        values = {
                            "product_id": product,
                            "location_id": location,
                            "inventory_quantity": int(qty),
                        }
                        adj_create = stock_adj.create(values)
                        adj_create._compute_inventory_diff_quantity()
                        count += 1
                        row += 1
            else:
                raise UserError(_("Please Select Excel File"))
        return {
            "effect": {
                "fadeout": "slow",
                "message": " {} Inventory Adjustment Imported!".format(str(count)),
                "img_url": "/web/static/src/img/smile.svg",
                "type": "rainbow_man",
            }
        }
