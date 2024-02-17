from odoo import models, fields

import xlrd
import base64
from datetime import datetime


class InvoiceImport(models.Model):
    _name = "invoice.import"
    _description = "Invoice Import"

    file = fields.Binary("File")

    def button_import(self):
        if self.file:
            wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))
            for sheet in wb.sheets():
                col_name = 1
                col_partner = 2
                col_invoice_date = 3
                col_currency = 4
                col_product = 5
                col_account = 6
                col_quantity = 8
                col_uom = 9
                col_description = 10
                col_unit_price = 11
                col_discount_amount = 12
                col_tax = 13
                for row in range(1, sheet.nrows):
                    name = sheet.cell(row, col_name).value
                    partner = sheet.cell(row, col_partner).value
                    invoice_date = float(sheet.cell(row, col_invoice_date).value)
                    currency = sheet.cell(row, col_currency).value
                    product = sheet.cell(row, col_product).value
                    account = sheet.cell(row, col_account).value
                    quantity = float(sheet.cell(row, col_quantity).value)
                    uom = sheet.cell(row, col_uom).value
                    description = sheet.cell(row, col_description).value
                    unit_price = float(sheet.cell(row, col_unit_price).value)
                    discount_amount = float(sheet.cell(row, col_discount_amount).value)
                    tax_name = sheet.cell(row, col_tax).value
                    discount = (discount_amount / (unit_price * quantity)) * 100 if discount_amount else 0.0
                    move_id = self.env["account.move"].search([("name", "=", name)])
                    product_id = self.env["product.product"].search([("name", "=", product)], limit=1)
                    account_id = self.env["account.account"].search([("name", "=", account)], limit=1)
                    tax_id = self.env["account.tax"].search([("description", "=", tax_name)], limit=1)
                    uom_id = self.env["uom.uom"].search([("name", "=", uom)], limit=1)
                    partner_id = self.env["res.partner"].search([("customer_code", "=", partner)], limit=1)
                    currency_id = self.env["res.currency"].search([("name", "=", currency)], limit=1)
                    seconds = (invoice_date - 25569) * 86400.0
                    invoice_date_formatted = datetime.utcfromtimestamp(seconds).date()
                    line = [
                        (
                            0,
                            0,
                            {
                                "product_id": product_id.id,
                                "name": description,
                                "account_id": account_id.id,
                                "quantity": float(quantity),
                                "product_uom_id": uom_id.id,
                                "price_unit": float(unit_price),
                                "discount_amount": float(discount_amount),
                                "discount": discount,
                                "tax_ids": [(6, 0, tax_id.ids)],
                            },
                        )
                    ]
                    if move_id:
                        move_id.invoice_line_ids = line
                    else:
                        self.env["account.move"].create(
                            {
                                "name": name,
                                "partner_id": partner_id.id,
                                "currency_id": currency_id.id,
                                "invoice_date": invoice_date_formatted,
                                "invoice_line_ids": line,
                                "move_type": "out_invoice",
                            }
                        )
