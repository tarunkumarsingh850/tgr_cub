from odoo import _, fields, models
from odoo.exceptions import UserError
import xlrd
import base64


class JournalLineWizard(models.TransientModel):
    _name = "journal.line.wizard"
    _description = "Model is used to update lines"

    journal_line_update_id = fields.Many2one("account.move")
    excel_file = fields.Binary(string="Excel File", attachment=True)

    def generate_template(self):
        return self.env.ref("bi_import_journal_line.action_export_template").report_action(self, config=False)

    def load_lines(self):
        for record in self:
            if record.excel_file:
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(record.excel_file))
                for sheet in workbook.sheets():
                    account_col = 0
                    partner_col = 1
                    label_col = 2
                    debit_col = 3
                    credit_col = 4
                    values = []
                    for row in range(1, sheet.nrows):
                        try:
                            account_id = self.env["account.account"].search(
                                [("code", "=", int(sheet.cell(row, account_col).value))], limit=1
                            )
                            if not account_id:
                                raise UserError(_("Account not found at row %s" % (row + 1)))
                            partner_id = False
                            partner = str(sheet.cell(row, partner_col).value).split(".")[0]
                            partner_id = self.env["res.partner"].search([("name", "=", partner)], limit=1)
                            label = False
                            label = sheet.cell(row, label_col).value
                            debit = False
                            debit = sheet.cell(row, debit_col).value
                            credit = False
                            credit = sheet.cell(row, credit_col).value
                            values.append(
                                (
                                    0,
                                    0,
                                    {
                                        "account_id": account_id.id,
                                        "partner_id": partner_id.id if partner_id else False,
                                        "name": label,
                                        "debit": debit if debit else 0,
                                        "credit": credit if credit else 0,
                                    },
                                )
                            )
                        except IndexError:
                            break
                    record.journal_line_update_id.line_ids = False
                    record.journal_line_update_id.line_ids = values
                    break
