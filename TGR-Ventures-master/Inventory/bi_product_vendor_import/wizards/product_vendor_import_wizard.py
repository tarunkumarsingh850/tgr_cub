from odoo import models, fields, _
from odoo.exceptions import UserError
import xlrd
import base64


class ProductVendorImportWizard(models.Model):
    _name = "product.vendor.import.wizard"
    _description = "Product Vendor Import Wizard"

    file = fields.Binary("File")

    def confirm(self):
        book = xlrd.open_workbook(file_contents=base64.decodestring(self.file))
        sku_col = 0
        vendor_col = 1
        currency_col = 2
        qty_col = 3
        price_col = 4
        lead_time_col = 5
        count = 0
        for sheet in book.sheets():
            for row in range(1, sheet.nrows):
                sku = sheet.cell(row, sku_col).value
                vendor_code = sheet.cell(row, vendor_col).value
                currency_name = sheet.cell(row, currency_col).value
                qty = sheet.cell(row, qty_col).value
                price = sheet.cell(row, price_col).value
                lead_time = sheet.cell(row, lead_time_col).value
                product = self.env["product.template"].search([("default_code", "=", sku)])
                if not product:
                    raise UserError(_(f"Product with SKU {sku} not found."))
                vendor = self.env["res.partner"].search([("vendor_code", "=", vendor_code), ("is_supplier", "=", True)])
                if not vendor:
                    raise UserError(_(f"Vendor with code {vendor_code} not found."))

                currency = self.env["res.currency"].search(
                    [
                        ("name", "=", currency_name),
                    ]
                )
                values = {"name": vendor.id}
                if qty:
                    values.update({"min_qty": float(qty)})
                if price:
                    values.update({"price": float(price)})
                if lead_time:
                    values.update({"delay": int(lead_time)})
                if currency:
                    values.update({"currency_id": currency.id})
                product.seller_ids.unlink()
                product.seller_ids = [(0, 0, values)]
                count += 1
        return {
            "effect": {
                "fadeout": "slow",
                "message": f"{count} records successfully imported",
                "img_url": "/web/static/img/smile.svg",
                "type": "rainbow_man",
            }
        }

    def export_template(self):
        return self.env.ref("bi_product_vendor_import.product_vendor_import_template").report_action(self, config=False)
