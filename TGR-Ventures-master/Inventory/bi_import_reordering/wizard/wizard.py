import base64
import xlrd
from odoo.exceptions import UserError
from odoo import fields, models, _


class ImportReordering(models.TransientModel):
    _name = "import.reordering"
    _description = "Import Reordering"

    excel_file = fields.Binary(
        "Upload Excel",
        attachment=True,
        help="Excel Column Format : SKU, Warehouse, Min Qty, Max Qty, To Order",
    )

    def export_template(self):
        return self.env.ref("bi_import_reordering.reordering_action_export_template").report_action(self, config=False)

    def import_xls(self):
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.excel_file))
        values = {}
        excel_heading = []
        count = 0
        sl_col = 0

        for sheet in wb.sheets():
            for i in range(0, sheet.nrows):
                for j in range(0, sheet.ncols):
                    if i == 0:
                        heading = sheet.cell(i, j).value
                        if heading in [
                            "SKU",
                            "Warehouse",
                            "Min Qty",
                            "Max Qty",
                        ]:
                            excel_heading.append(heading)
                        else:
                            raise UserError(_("Incorrect Excel format %s") % heading)
                    else:
                        max_qty = 0
                        min_qty = 0
                        if sheet.cell(i, sl_col).value:
                            if excel_heading[j] == "SKU":
                                sku = sheet.cell(i, j).value
                                product_id = self.env["product.product"].search([("default_code", "=", sku)], limit=1)
                                if product_id:
                                    values["product_id"] = product_id.id
                                else:
                                    raise UserError(_("'%s' not a valid Product SKU") % (sku))
                            elif excel_heading[j] == "Warehouse":
                                warehouse = sheet.cell(i, j).value
                                warehouse_id = self.env["stock.warehouse"].search([("name", "=", warehouse)], limit=1)
                                if warehouse_id:
                                    values["warehouse_id"] = warehouse_id.id
                                    values["location_id"] = warehouse_id.lot_stock_id.id
                                else:
                                    raise UserError(_("'%s' not a valid Warehouse") % (warehouse))
                            elif excel_heading[j] == "Min Qty":
                                min_qty = sheet.cell(i, j).value
                                if type(min_qty) == float:
                                    min_qty = int(min_qty)
                                values["product_min_qty"] = str(min_qty)
                            elif excel_heading[j] == "Max Qty":
                                max_qty = sheet.cell(i, j).value
                                if type(max_qty) == float:
                                    max_qty = int(max_qty)
                                values["product_max_qty"] = str(max_qty)

                if values:
                    values["trigger"] = "auto"
                    self.env["stock.warehouse.orderpoint"].sudo().create(values)
                    count += 1
                    values = {}

        return {
            "effect": {
                "fadeout": "slow",
                "message": " {} Reordering Order Imported!".format(str(count)),
                "img_url": "/web/static/src/img/smile.svg",
                "type": "rainbow_man",
            }
        }
