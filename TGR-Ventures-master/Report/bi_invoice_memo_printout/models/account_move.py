from odoo import fields, models
import datetime


class Accountmove(models.Model):
    _inherit = "account.move"


    def get_currency_convert_amount(self, amount):
        convert_currency_id = self.get_currency_id()
        convert_amount = self.currency_id.with_context(date=datetime.datetime.today()).compute(amount, convert_currency_id)
        return convert_amount and round(convert_amount, 2) or 0.00


    def get_currency_id(self):
        currency_id = self.env['res.currency'].search([('name','=','GBP')], limit=1)
        return currency_id