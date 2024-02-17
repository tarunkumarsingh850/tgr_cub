from odoo import fields, models,_
from odoo.exceptions import UserError
import base64
import xlrd
import os
from datetime import datetime


class SalePriceUpdateWizard(models.TransientModel):
    _name = "ez.invoice.import.wizard"

    filename = fields.Char(string="File name")
    csv_file = fields.Binary("Upload File", attachment=True)
    partner_id = fields.Many2one('res.partner', 'Customer', domain="[('is_ez_import_customer','=', True)]")
    currency_id = fields.Many2one("res.currency", string="Currency")

    def generate_template(self):
        return self.env.ref("bi_ez_invoice_import.action_export_template").report_action(self, config=False)

    def generate_update(self):
        count = 0
        if self.csv_file:
            file_value = self.csv_file.decode("utf-8")
            filename, FileExtension = os.path.splitext(self.filename)
            if FileExtension == ".csv":
                input_file = base64.b64decode(file_value)
                lst = []
                for loop in input_file.decode("utf-8"):
                    lst.append(loop)
                lsts = input_file.decode("utf-8").split("\n")
                lsts.pop(0)
                # print (sdf)
                for rec in lsts:
                    if rec:
                        code = rec.split(",")

                        partner_id = self.env["res.partner"].search([("name", "=", code[8])], limit=1)
                        if not partner_id:
                            partner_id = self.env["res.partner"].create({"name": code[8]})
                        country_id = self.env["res.country"].search([("code", "=", code[2])], limit=1)
                        if not country_id:
                            country_id = self.env["res.country"].create({"code": code[2], "name": code[2]})

                        if country_id and partner_id:
                            partner_id.type = "delivery"
                            partner_id.country_id = country_id

                        journal_id = self.env["account.journal"].search([("type", "=", "sale")], limit=1)

                        line_id = []
                        account_id = self.env["account.account"].search([("name", "=", code[3])], limit=1)
                        if account_id:
                            line_id.append((0, 0, {"account_id": account_id}))

                        invoice_line = []
                        tax_id = self.env["account.tax"].search([("name", "=", code[7])], limit=1)
                        if taxable_amount_euro:
                            invoice_line.append(
                                (0, 0, {"price_unit": code[4], "quantity": 1, "tax_ids": [(4, tax_id)]})
                            )

                        move_id = self.env["account.move"]
                        move_id.create(
                            {
                                "invoice_date": invoice_date,
                                "ref": account_move_name,
                                "move_type": "out_invoice",
                                "parnter_id": partner_id,
                                "journal_id": journal_id,
                                "line_ids": line_id,
                                "invoice_line_ids": invoice_line,
                            }
                        )
            else:
                wb = xlrd.open_workbook(file_contents=base64.decodestring(self.csv_file))
                move_id_rno = 1
                invocie_date_rno = 0
                delivery_country_rno = 2
                account_rno = 3
                taxable_amount_euro_rno = 4
                total_amount_euro_rno = 5
                customer_jouranl_id_rno = 6
                tax_rate_rno = 7
                customer_rno = 8

                move_id = self.env["account.move"]
                for sheet in wb.sheets():
                    for row in range(1, sheet.nrows):

                        account_move_name = (isinstance(sheet.cell(row, move_id_rno).value, float) and int(sheet.cell(row, move_id_rno).value) or sheet.cell(row, move_id_rno).value) or ''

                        invoice_date = sheet.cell(row, invocie_date_rno).value or ""
                        seconds = (invoice_date - 25569) * 86400.0
                        invoice_date_formatted = datetime.utcfromtimestamp(seconds).date()
                        delivery_country = sheet.cell(row, delivery_country_rno).value   or ""
                        account_name = sheet.cell(row, account_rno).value or ""

                        taxable_amount_euro = sheet.cell(row, taxable_amount_euro_rno).value or ""
                        sheet.cell(row, total_amount_euro_rno).value or ""
                        sheet.cell(row, customer_jouranl_id_rno).value or ""
                        tax_rate = sheet.cell(row, tax_rate_rno).value or ""
                        customer_name = sheet.cell(row, customer_rno).value or ""

                        country_id = self.env["res.country"].search([("code", "=", delivery_country.upper())], limit=1)
                        if not country_id:
                            country_id = self.env["res.country"].create(
                                {"code": delivery_country.upper(), "name": delivery_country}
                            )
                        partner_id = self.env["res.partner"].search([("name", "=", customer_name)], limit=1)
                        if not partner_id:
                            partner_id = self.env["res.partner"].create(
                                {
                                    "name": customer_name,
                                    "company_type": "person",
                                    "type": "delivery",
                                    "country_id": country_id.id,
                                }
                            )
                        partner_shipping_id = self.env["res.partner"].search([("parent_id", "=", self.partner_id.id), ("country_id","=", country_id.id,)], limit=1)
                        if not partner_shipping_id:
                            partner_shipping_id = self.env["res.partner"].create(
                                {
                                    "name": customer_name,
                                    "company_type": "person",
                                    "type": "delivery",
                                    "country_id": country_id.id,
                                    'parent_id': self.partner_id.id
                                }
                            )
                        journal_id = self.env["account.journal"].search([("type", "=", "sale")], limit=1)

                        line_id = []
                        account_id = self.env["account.account"].search(
                            [("code", "ilike", account_name and int(account_name) or False)], limit=1
                        )

                        invoice_line = []
                        tax_id = self.env["account.tax"].search([("name", "ilike", tax_rate)], limit=1)
                        if not tax_id:
                            raise UserError(_(f'Tax Rate "{tax_rate}"  at row {row+1} not found'))
                        invoice_line.append(
                            (
                                0,
                                0,
                                {
                                    "name": account_id and account_id.name or "",
                                    "account_id": account_id and account_id.id or "",
                                    "price_unit": taxable_amount_euro and taxable_amount_euro or 0.00,
                                    "quantity": 1,
                                    "tax_ids": tax_id and [(4, tax_id.id)],
                                },
                            )
                        )

                        addr = partner_id.address_get(['delivery'])
                        addr['delivery'] = partner_shipping_id.id
                        move_id=self.env['account.move'].with_context(is_ez_import = True,account_id=account_id.id).create(
                            {
                                "invoice_date": invoice_date_formatted or datetime.now(),
                                "ref": account_move_name,
                                "move_type": "out_invoice",
                                "partner_id": partner_id.id,
                                "journal_id": journal_id.id,
                                "invoice_line_ids": invoice_line,
                                "partner_shipping_id": addr and addr.get('delivery'),
                                "currency_id":self.currency_id and self.currency_id.id or self.env.company.currency_id.id
                            }
                        )
                        move_id.partner_shipping_id = partner_shipping_id.id
                        count += 1
        return {
            "effect": {
                "fadeout": "slow",
                "message": f"{count} records successfully imported",
                "img_url": "/web/static/img/smile.svg",
                "type": "rainbow_man",
            }
        }
