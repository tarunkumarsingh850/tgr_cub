from odoo import _, fields, models
from odoo.exceptions import UserError
import xlrd
import base64


class StockUpdateWizard(models.TransientModel):
    _name = "purchase.update.wizard"
    _description = "Model is used to update lines"

    purchase_update_id = fields.Many2one("purchase.order")
    excel_file = fields.Binary(string="Excel File", attachment=True)

    def load_lines(self):
        for record in self:
            if record.excel_file:
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(record.excel_file))
                count = 0
                for sheet in workbook.sheets():
                    product_col = 0
                    supplier_sku_col = 1
                    warehouse_col = 2
                    qty_col = 3
                    unit_col = 4
                    tax_col = 5
                    dest_warehouse = False
                    dest_location = False
                    values = []
                    for row in range(1, sheet.nrows):
                        taxes_list = []
                        try:
                            product_id = self.env["product.product"].search(
                                [("default_code", "=", sheet.cell(row, product_col).value)], limit=1
                            )
                            if not product_id:
                                raise UserError(_("Product not found at row %s" % (row + 1)))

                            product_qty = False
                            unit_price = False
                            unit_price = sheet.cell(row, unit_col).value
                            if not unit_price:
                                if product_id.standard_price:
                                    unit_price = product_id.standard_price
                                elif product_id.product_tmpl_id.last_cost_2:
                                    unit_price = product_id.product_tmpl_id.last_cost_2
                            product_qty = sheet.cell(row, qty_col).value

                            warehouse = sheet.cell(row, warehouse_col).value
                            if warehouse:
                                warehouse_id = self.env["stock.warehouse"].search(
                                    [("name", "ilike", warehouse)], limit=1
                                )

                                if warehouse_id:
                                    # if record.purchase_update_id and \
                                    #         record.purchase_update_id.picking_type_id and \
                                    #         record.purchase_update_id.picking_type_id.warehouse_id:
                                    #     raise UserError(_("Warehouse not match! Deliver To have %s warehouse while in the Sheet warehouse is %s") % (record.purchase_update_id.picking_type_id.warehouse_id.name,warehouse))
                                    dest_warehouse = warehouse_id.id
                                    dest_location = warehouse_id.lot_stock_id.id
                                # else:
                                #     raise UserError(_("Warehouse not found at row %s" % (row + 1)))
                            elif self.env.company.id == 10 and product_id.default_warehouse_id:
                                dest_warehouse = product_id.default_warehouse_id.id
                                dest_location = product_id.default_warehouse_id.lot_stock_id.id
                            else:
                                dest_warehouse = self.purchase_update_id.picking_type_id.warehouse_id.id
                                dest_location = self.purchase_update_id.picking_type_id.warehouse_id.lot_stock_id.id
                            supplier_sku = sheet.cell(row, supplier_sku_col).value
                            if supplier_sku:
                                supplier_sku_no = supplier_sku
                            else:
                                supplier_sku_no = product_id.supplier_sku_no
                            taxes = sheet.cell(row, tax_col).value
                            if taxes:
                                tax = str(taxes).split(",")
                                for t in tax:
                                    t_list = t.split(".")
                                    account_tax_id = self.env["account.tax"].search(
                                        [("code", "=", int(t_list[0]))], limit=1
                                    )
                                    if t:
                                        if account_tax_id:
                                            taxes_list.append(account_tax_id.id)
                                        else:
                                            raise UserError(_("'%s' not a Tax") % (t))
                            else:
                                taxes_list = self.purchase_update_id.partner_id.mapped("taxes_ids").ids

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
                                        "supplier_sku_no": supplier_sku_no,
                                        "price_unit": unit_price,
                                        "taxes_id": [(6, 0, taxes_list)],
                                    },
                                )
                            )
                            count += 1
                        except IndexError:
                            break
                    record.purchase_update_id.order_line = False
                    record.purchase_update_id.order_line = values
                    break
        return {
            "effect": {
                "fadeout": "slow",
                "message": f"{count} records successfully imported",
                "img_url": "/web/static/img/smile.svg",
                "type": "rainbow_man",
            }
        }
