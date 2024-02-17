from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    customer_order = fields.Char("Customer Order")

    def button_print_excel(self):
        data = {
            "ids": self.ids,
            "model": self._name,
        }
        return self.env.ref("bi_invoice_excel_report.action_view_invoice_excel1").report_action(
            self, data=data, config=False
        )

    def button_print_memo_excel(self):
        data = {
            "ids": self.ids,
            "model": self._name,
        }
        return self.env.ref("bi_invoice_excel_report.action_view_invoice_memo_excel1").report_action(
            self, data=data, config=False
        )

    # @api.depends("product_id")
    # def _compute_pack_size(self):
    #     for each in self:
    #         if each.product_id:
    #             each.pack_size = each.product_id.pack_size_desc
    #         else:
    #             each.pack_size = ""
