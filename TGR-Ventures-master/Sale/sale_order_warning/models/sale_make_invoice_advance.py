from odoo import _, models
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        sale_orders = self.env["sale.order"].browse(self._context.get("active_ids", []))
        if sale_orders:
            for record in sale_orders:
                if record.partner_id.credit > record.partner_id.credit_limit:
                    # if record.no_credit_issue is False:
                    raise UserError(_("Credit Limit exceeds.You cannot create invoice."))
        rec = super(SaleAdvancePaymentInv, self).create_invoices()
        return rec
