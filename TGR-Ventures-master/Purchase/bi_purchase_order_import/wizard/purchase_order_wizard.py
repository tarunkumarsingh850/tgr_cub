from odoo import _, fields, models
from odoo.exceptions import UserError
import xlrd
import base64


class StockUpdateWizard(models.TransientModel):
    _name = "purchase.order.update.wizard"
    _description = "Model is used to update"

    excel_file = fields.Binary(string="Excel File", attachment=True)

    def export_lpo_template(self):
        return self.env.ref("bi_purchase_order_import.action_export_lpo_template").report_action(self, config=False)

    def load_lines(self):
        for record in self:
            if record.excel_file:
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(record.excel_file))
                count = 0
                for sheet in workbook.sheets():
                    po_obj = self.env["purchase.order"]
                    vendor_col = 0
                    product_col = 1
                    warehouse_col = 2
                    qty_col = 3
                    unit_col = 4
                    dest_warehouse = False
                    dest_location = False
                    vendor_list = []
                    for row in range(1, sheet.nrows):
                        values = []
                        try:
                            vendor = sheet.cell(row, vendor_col).value
                            if vendor not in vendor_list:
                                vendor_list.append(vendor)
                                for each_row in range(1, sheet.nrows):
                                    vendor_each = sheet.cell(each_row, vendor_col).value
                                    if vendor_each == vendor:
                                        vendor_id = self.env["res.partner"].search(
                                            [("name", "=", sheet.cell(row, vendor_col).value)], limit=1
                                        )
                                        if not vendor_id:
                                            raise UserError(_("Vendor not found at row %s" % (each_row + 1)))
                                        product_id = self.env["product.product"].search(
                                            [("default_code", "=", sheet.cell(each_row, product_col).value)], limit=1
                                        )
                                        if not product_id:
                                            raise UserError(_("Product not found at row %s" % (each_row + 1)))
                                        product_qty = False
                                        unit_price = False
                                        warehouse = sheet.cell(each_row, warehouse_col).value
                                        if warehouse:
                                            warehouse_id = self.env["stock.warehouse"].search(
                                                [("name", "ilike", warehouse)], limit=1
                                            )
                                            if warehouse_id:
                                                dest_warehouse = warehouse_id.id
                                                dest_location = warehouse_id.lot_stock_id.id
                                            else:
                                                raise UserError(_("Warehouse not found at row %s" % (each_row + 1)))

                                        unit_price = sheet.cell(each_row, unit_col).value
                                        product_qty = sheet.cell(each_row, qty_col).value
                                        values.append(
                                            (
                                                0,
                                                0,
                                                {
                                                    "product_id": product_id.id,
                                                    "product_uom": product_id.uom_id.id,
                                                    "warehouse_dest_id": dest_warehouse,
                                                    "location_dest_id": dest_location,
                                                    "product_qty": product_qty,
                                                    "price_unit": unit_price,
                                                },
                                            )
                                        )
                                    else:
                                        continue
                                    each_row += 1
                                values = {
                                    "partner_id": vendor_id.id,
                                    "order_line": values,
                                }
                                po = po_obj.create(values)
                                po._onchange_eta_date()
                                count += 1
                        except IndexError:
                            break
                        row += 1
                    break
        return {
            "effect": {
                "fadeout": "slow",
                "message": f"{count} records successfully imported",
                "img_url": "/web/static/img/smile.svg",
                "type": "rainbow_man",
            }
        }
