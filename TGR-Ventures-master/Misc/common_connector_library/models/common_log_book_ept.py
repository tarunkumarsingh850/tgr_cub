# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class CommonLogBookEpt(models.Model):
    _name = "common.log.book.ept"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _description = "Common log book Ept"

    name = fields.Char(readonly=True)
    type = fields.Selection([("import", "Import"), ("export", "Export")], string="Operation")
    module = fields.Selection(
        [
            ("amazon_ept", "Amazon Connector"),
            ("woocommerce_ept", "Woocommerce Connector"),
            ("shopify_ept", "Shopify Connector"),
            ("magento_ept", "Magento Connector"),
            ("bol_ept", "Bol Connector"),
            ("ebay_ept", "Ebay Connector"),
            ("amz_vendor_central", "Amazon Vendor Central"),
        ]
    )
    active = fields.Boolean(default=True)
    log_lines = fields.One2many("common.log.lines.ept", "log_book_id")
    message = fields.Text()
    model_id = fields.Many2one("ir.model", help="Model Id", string="Model")
    res_id = fields.Integer(string="Record ID", help="Process record id")
    attachment_id = fields.Many2one("ir.attachment", string="Attachment")
    file_name = fields.Char()
    sale_order_id = fields.Many2one(comodel_name="sale.order", string="Sale Order")
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company.id)
    is_data_import_log_book = fields.Boolean(
        string="Log book for data importing",
    )

    @api.model
    def create(self, vals):
        """To generate a sequence for a common logbook.
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 23 September 2021 .
        Task_id: 178058
        """
        sequences = self.env["ir.sequence"].search(
            [("company_id", "=", self.env.company.id), ("name", "=", "Log Book")]
        )
        if not sequences:
            sequence_obj = (
                self.env["ir.sequence"]
                .sudo()
                .create(
                    {
                        "company_id": self.env.company.id,
                        "padding": 6,
                        "name": "Log Book",
                    }
                )
            )
            end_code = sequence_obj.next_by_id(sequence_obj.id)
        else:
            end_code = sequences.next_by_id(sequences.id)

        name = f"Log Book/{end_code}"
        vals["name"] = name
        return super(CommonLogBookEpt, self).create(vals)

    def create_common_log_book(self, process_type, instance_field, instance, model_id, module):
        """This method used to create a log book record.
        @param process_type: Generally, the process type value is 'import' or 'export'.
        @param : Name of the field which relates to the instance field for different apps.
        @param instance: Record of instance.
        @param model_id: Model related to log, like create a sales order related log then pass the sales order
        model.
        @param module: For which App this log book is belongs to.
        @return: Record of log book.
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 23 September 2021 .
        Task_id:
        """
        log_book_id = self.create(
            {"type": process_type, "module": module, instance_field: instance.id, "model_id": model_id, "active": True}
        )
        return log_book_id
