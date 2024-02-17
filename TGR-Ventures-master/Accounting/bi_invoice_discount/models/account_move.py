from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount_amount = fields.Monetary("Discount Amount", digits="Product Price", default=0.0)

    @api.onchange("discount_amount", "quantity", "price_unit")
    def _onchange_discount_amount(self):
        for each in self:
            each.discount = 0
            if each.discount_amount:
                dis_percent = each.quantity * each.price_unit and (each.discount_amount / (each.quantity * each.price_unit)) * 100 or 0.00
                each.discount = dis_percent

    @api.onchange("quantity", "price_unit", "discount")
    def _onchange_discount_amount_percentage(self):
        for each in self:
            if each.discount:
                dis_percent = (each.quantity * each.price_unit) * (each.discount / 100)
                each.discount_amount = dis_percent
