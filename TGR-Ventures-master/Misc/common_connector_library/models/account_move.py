# See LICENSE file for full copyright and licensing details.
from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_invoice_origin(self):
        records = self.env["account.move"].search(
            [("move_type", "=", "out_invoice"), ("state", "in", ("posted", "draft"))]
        )
        for record in records:
            if record.invoice_origin:
                sale_id = self.env["sale.order"].search([("name", "=", record.invoice_origin)])
                if sale_id:
                    if not record.magento_website_id:
                        record.magento_website_id = sale_id.magento_website_id.id

    def action_change_lines(self):
        records = self.env["account.move"].search(
            [("move_type", "=", "out_invoice"), ("state", "in", ("posted", "draft"))]
        )
        for record in records:
            if record.magento_website_id.income_account_id:
                if record.invoice_line_ids:
                    for line in record.invoice_line_ids:
                        if line.product_id.detailed_type == "product":
                            line.update({"account_id": record.magento_website_id.income_account_id.id})

    def action_change_lines_discount(self):
        records = self.env["account.move"].search(
            [("move_type", "=", "out_invoice"), ("state", "in", ("posted", "draft"))]
        )
        for record in records:
            if record.magento_website_id.income_account_id:
                if record.invoice_line_ids:
                    for line in record.invoice_line_ids:
                        if line.product_id.default_code == "MAGENTO DISCOUNT":
                            line.update({"account_id": record.magento_website_id.income_account_id.id})

    def action_change_lines_deliveryisurance(self):
        records = self.env["account.move"].search(
            [("move_type", "=", "out_invoice"), ("state", "in", ("posted", "draft"))]
        )
        for record in records:
            if record.magento_website_id.delivery_isurance_account_id:
                if record.invoice_line_ids:
                    for line in record.invoice_line_ids:
                        if line.product_id.default_code == "DeliveryIsurance":
                            line.update({"account_id": record.magento_website_id.delivery_isurance_account_id.id})

    def action_change_shopify_accounts(self):
        records = self.env["account.move"].search(
            [("move_type", "=", "out_invoice"), ("state", "in", ("posted", "draft"))]
        )
        for record in records:
            if record.shopify_instance_id:
                if record.invoice_line_ids:
                    for line in record.invoice_line_ids:
                        if record.shopify_instance_id.income_account_id and line.product_id.detailed_type == "product":
                            line.update({"account_id": record.shopify_instance_id.income_account_id.id})

    def action_change_lines_shipment(self):
        records = self.env["account.move"].search(
            [("move_type", "=", "out_invoice"), ("state", "in", ("posted", "draft"))]
        )
        for record in records:
            if record.magento_website_id.income_account_id:
                if record.invoice_line_ids:
                    for line in record.invoice_line_ids:
                        if line.product_id.default_code == "MAGENTO_SHIP":
                            line.update({"account_id": record.magento_website_id.shipment_account_id.id})

    @api.model
    def _get_default_journal(self):
        res = super(AccountMove, self)._get_default_journal()
        if self._context.get("journal_ept"):
            res = self._context.get("journal_ept")
        return res

    def prepare_payment_dict(self, work_flow_process_record):
        """This method use to prepare a vals dictionary for payment.
        @param work_flow_process_record: Record of auto invoice workflow.
        @return: Dictionary of payment vals
        @author: Twinkalc.
        Migration done by Haresh Mori on September 2021
        """
        return {
            "journal_id": work_flow_process_record.journal_id.id,
            "ref": self.payment_reference,
            "currency_id": self.currency_id.id,
            "payment_type": "inbound",
            "date": self.date,
            "partner_id": self.commercial_partner_id.id,
            "amount": self.amount_residual,
            "payment_method_id": work_flow_process_record.inbound_payment_method_id.id,
            "partner_type": "customer",
        }
