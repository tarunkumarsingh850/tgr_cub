from odoo import models, fields, _
from odoo.exceptions import UserError
import xlrd
import base64
from datetime import datetime


class TransactionLineWizard(models.Model):
    _name = "transaction.line.wizard"

    bank_statement_line_id = fields.Many2one("account.bank.statement")
    excel_file = fields.Binary("Excel File")

    def export_template(self):
        return self.env.ref("bi_import_account_bank_statement.action_export_template").report_action(self, config=False)

    def load_lines(self):
        for record in self:
            if record.excel_file:
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(record.excel_file))
                for sheet in workbook.sheets():
                    date_col = 0
                    label_col = 1
                    partner_col = 2
                    amount_col = 3
                    values = []
                    for row in range(1, sheet.nrows):
                        try:
                            label = False
                            label = sheet.cell(row, label_col).value
                            amount = False
                            amount = sheet.cell(row, amount_col).value
                            partner = False
                            partner = str(sheet.cell(row, partner_col).value).split(".")[0]
                            partner_id = self.env["res.partner"].search([("name", "=", partner)], limit=1)
                            date = False
                            date = sheet.cell(row, date_col).value
                            if isinstance(date, str):
                                date_format = datetime.strptime(date, "%d/%m/%Y")
                            elif isinstance(date, float):
                                seconds = (date - 25569) * 86400.0
                                date_format = datetime.utcfromtimestamp(seconds)
                            else:
                                raise UserError(_("Wrong format for date found at row %s" % (row + 1)))
                            if not date:
                                raise UserError(_("Date not found at row %s" % (row + 1)))
                            values.append(
                                (
                                    0,
                                    0,
                                    {
                                        "date": date_format,
                                        "partner_id": partner_id.id if partner_id else False,
                                        "payment_ref": label,
                                        "amount": amount,
                                    },
                                )
                            )
                        except IndexError:
                            break
                    record.bank_statement_line_id.line_ids = False
                    record.bank_statement_line_id.line_ids = values
                    break
