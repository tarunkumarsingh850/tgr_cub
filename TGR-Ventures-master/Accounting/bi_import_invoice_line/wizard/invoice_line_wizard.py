from odoo import _, fields, models
from odoo.exceptions import UserError
import xlrd
import base64


class InvoiceLineWizard(models.TransientModel):
    _name = "invoice.line.wizard"
    _description = "Model is used to update lines"

    invoice_line_update_id = fields.Many2one("account.move")
    excel_file = fields.Binary(string="Excel File", attachment=True)

    def export_template_invoice(self):
        return self.env.ref("bi_import_invoice_line.action_export_template").report_action(self, config=False)

    def load__invoice_lines(self):
        for record in self:
            if record.excel_file:
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(record.excel_file))
                for sheet in workbook.sheets():
                    sku_col = 0
                    quantity_col = 1
                    price_col = 2
                    tax_col = 3
                    dis_col = 4
                    values = []
                    taxes_list = []
                    for row in range(1, sheet.nrows):
                        try:
                            product_id = self.env["product.product"].search(
                                [("default_code", "=", sheet.cell(row, sku_col).value)], limit=1
                            )
                            if not product_id:
                                raise UserError(_("Product not found at row %s" % (row + 1)))
                            taxes = False
                            taxes = sheet.cell(row, tax_col).value
                            taxes_list = []
                            if taxes:
                                tax = taxes.split(",")
                                for t in tax:
                                    account_tax_id = self.env["account.tax"].search([("name", "=", t)], limit=1)
                                    if t:
                                        if account_tax_id:
                                            taxes_list.append(account_tax_id.id)
                            quantity = False
                            quantity = sheet.cell(row, quantity_col).value
                            price = False
                            price = sheet.cell(row, price_col).value
                            discount = False
                            discount = sheet.cell(row, dis_col).value
                            line_account = False
                            if self.invoice_line_update_id.move_type == "out_invoice":
                                line_account = product_id.categ_id.property_account_income_categ_id.id
                            elif self.invoice_line_update_id.move_type == "in_invoice":
                                line_account = product_id.categ_id.property_account_expense_categ_id.id
                            values.append(
                                (
                                    0,
                                    0,
                                    {
                                        "product_id": product_id.id,
                                        "name": product_id.name,
                                        "account_id": line_account,
                                        "quantity": quantity,
                                        "price_unit": price,
                                        "tax_ids": [(6, 0, taxes_list)],
                                        "discount": discount if discount else False,
                                        "product_uom_id": product_id.uom_id.id,
                                        "pack_size": product_id.pack_size_desc,
                                    },
                                )
                            )
                        except IndexError:
                            break
                    record.invoice_line_update_id.invoice_line_ids = False
                    record.invoice_line_update_id.invoice_line_ids = values
                    break

        return {
            "effect": {
                "fadeout": "slow",
                "message": f"{len(values)} records successfully imported",
                "img_url": "/web/static/img/smile.svg",
                "type": "rainbow_man",
            }
        }
