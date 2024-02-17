from odoo import _, fields, models
from odoo.exceptions import UserError
import xlrd
import base64


class StockImportWizard(models.TransientModel):
    _name = "stock.import.wizard"
    _description = "Model is used to update lines"

    stock_picking_update_id = fields.Many2one("stock.picking")
    excel_file = fields.Binary(string="Excel File", attachment=True)

    def load_lines(self):
        for record in self:
            if record.excel_file:
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(record.excel_file))
                for sheet in workbook.sheets():
                    sku_col = 0
                    qty_col = 1
                    values = []
                    for row in range(1, sheet.nrows):
                        try:
                            product_id = self.env["product.product"].search(
                                [("default_code", "=", sheet.cell(row, sku_col).value)], limit=1
                            )
                            if not product_id:
                                raise UserError(_("Product not found at row %s" % (row + 1)))
                            product_qty = False
                            product_qty = sheet.cell(row, qty_col).value
                            if record.stock_picking_update_id.location_id:
                                source_location = record.stock_picking_update_id.location_id
                            else:
                                raise UserError(_("Source Location is not found!"))
                            if record.stock_picking_update_id.location_dest_id:
                                destination_location = record.stock_picking_update_id.location_dest_id
                            else:
                                raise UserError(_("Destination Location is not found!"))
                            values.append(
                                (
                                    0,
                                    0,
                                    {
                                        "product_id": product_id.id,
                                        "name": product_id.name,
                                        "product_uom": product_id.uom_id.id,
                                        "product_uom_qty": product_qty,
                                        "location_id": source_location.id,
                                        "location_dest_id": destination_location.id,
                                    },
                                )
                            )
                        except IndexError:
                            break
                    record.stock_picking_update_id.move_ids_without_package = False
                    record.stock_picking_update_id.move_ids_without_package = values
                    break
