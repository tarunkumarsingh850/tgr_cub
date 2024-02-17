from odoo import fields, models


class SyncMultiTransactionTaxJar(models.TransientModel):
    _name = "sync.multi.transaction.taxjar"
    _description = "Sync Multi Transaction TaxJar"

    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")

    def export_transaction_taxjar(self):
        self.ensure_one()
        invoices = self.env["account.move"].search(
            [
                ("invoice_date", ">=", self.from_date),
                ("invoice_date", "<=", self.to_date),
                ("is_sync_with_taxjar", "=", False),
                ("move_type", "in", ["out_invoice", "out_refund"]),
                ("state", "in", ["posted"]),
            ]
        )
        invoices = invoices.filtered(
            lambda x: x.fiscal_position_id
            and x.fiscal_position_id.taxjar_account_id
            and x.fiscal_position_id.taxjar_account_id.state == "confirm"
        )
        invoices.export_transaction_to_taxjar()
        return True
