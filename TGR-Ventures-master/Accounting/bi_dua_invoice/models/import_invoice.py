from odoo import models, fields, api, _


class ImportInvoice(models.Model):
    _name = "import.invoice"
    _description = "Import Invoice"

    name = fields.Char("Name", default="New", copy=False)
    move_id = fields.Many2one("account.move", string="Bill", copy=False)
    state = fields.Selection([("draft", "Draft"), ("sent", "Sent")], string="state", copy=False, default="draft")
    ref = fields.Char("Reference", copy=False)
    date = fields.Date("Date", default=fields.Date.today(), copy=False)
    vendor_id = fields.Many2one("res.partner", string="Vendor", copy=False)
    currency_id = fields.Many2one("res.currency", string="Currency", related="move_id.currency_id")
    amount = fields.Monetary("Amount", default=0.0, copy=False)
    tax_id = fields.Many2one("account.tax", string="Tax", copy=False)
    tax_amount = fields.Monetary("Tax Amount", compute="_compute_amount")
    amount_total = fields.Monetary("Amount Total", compute="_compute_amount")
    document_id = fields.Many2one("account.edi.document", string="Document", copy=False)
    error_message = fields.Char("Error Message", copy=False)

    @api.depends("amount", "tax_id")
    def _compute_amount(self):
        for rec in self:
            rec.amount_total = 0.0
            rec.tax_amount = 0.0
            tax = rec.tax_id.compute_all(rec.amount, rec.currency_id, quantity=1, partner=rec.vendor_id)
            rec.amount_total = tax["total_included"]
            rec.tax_amount = tax["total_included"] - tax["total_excluded"]

    def submit(self):
        for rec in self:
            if rec.move_id and rec.move_id.edi_document_ids:
                rec.move_id.edi_document_ids.unlink()
            for edi_format in rec.move_id.journal_id.edi_format_ids:
                document_id = self.env["account.edi.document"].create(
                    {
                        "edi_format_id": edi_format.id,
                        "move_id": rec.move_id.id,
                        "state": "to_send",
                    }
                )
                rec.document_id = document_id.id
                document_id._process_documents_web_services()

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("import.invoice") or _("New")
        res = super(ImportInvoice, self).create(vals)
        return res
