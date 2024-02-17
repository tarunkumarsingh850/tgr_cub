from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_credit_limit_exceed = fields.Boolean(default=False, copy=False)
    is_credit_on_hold = fields.Boolean(string="Is Credit ON Hold", default=False)
    no_credit_issue = fields.Boolean(string="Don't Consider Credit in this Order", default=False)

    # @api.onchange("partner_id")
    # def _onchange_partner_id(self):
    #     self.is_credit_limit_exceed = False
    #     if self.partner_id:
    #         today = date.today()
    #         move_id = self.env["account.move"].search(
    #             [
    #                 ("partner_id", "=", self.partner_id.id),
    #                 ("payment_state", "=", "not_paid"),
    #                 ("invoice_date_due", "<", today),
    #             ]
    #         )
    #         if move_id:
    #             if sum(move_id.mapped("amount_total")) > self.partner_id.credit_limit:
    #                 self.is_credit_limit_exceed = True

    @api.onchange("partner_id", "amount_total")
    def _onchange_credit_on_hold(self):
        if self.partner_id:
            credit = self.partner_id.credit
            credit_limit = self.partner_id.credit_limit
            if credit > credit_limit:
                self.is_credit_on_hold = True
            else:
                self.is_credit_on_hold = False

            # total = self.amount_total + self.partner_id.available_credit
            # if total > self.partner_id.credit_limit:
            #     self.is_credit_on_hold = True
            # elif total < 0:
            #     self.is_credit_on_hold = True
            # else:
            #     self.is_credit_on_hold = False
