from odoo import api, fields, models
from odoo.osv.expression import AND


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    website_ids = fields.Many2many(
        string="Website", comodel_name="magento.website", compute="_compute_website_ids", store=True
    )
    state = fields.Selection(selection_add=[("lock", "Lock")], ondelete={"lock": "set default"})
    operation_count = fields.Float(string="Transfer Count", compute="compute_operation_count")

    @api.depends("picking_ids")
    def _compute_website_ids(self):

        for record in self:
            website_ids = []
            for picking in record.picking_ids:
                if picking.magento_website_id:
                    if picking.magento_website_id.id not in website_ids:
                        website_ids.append(picking.magento_website_id.id)
            record.website_ids = [(6, 0, website_ids)]

    def action_lock(self):
        for rec in self:
            rec.write({"state": "lock"})

    def action_unlock(self):
        for rec in self:
            rec.write({"state": "draft"})

    @api.depends("picking_ids")
    def compute_operation_count(self):
        for rec in self:
            rec.operation_count = 0
            if rec.picking_ids:
                rec.operation_count = len(rec.picking_ids)

    @api.depends("company_id", "picking_type_id", "state")
    def _compute_allowed_picking_ids(self):
        """
        Override the base function for added processing_batched state.
        Returns:

        """
        allowed_picking_states = ["waiting", "confirmed", "assigned", "processing_batched"]

        for batch in self:
            domain_states = list(allowed_picking_states)
            # Allows to add draft pickings only if batch is in draft as well.
            if batch.state == "draft":
                domain_states.append("draft")
            domain = [
                ("company_id", "=", batch.company_id.id),
                ("state", "in", domain_states),
            ]
            if not batch.is_wave:
                domain = AND([domain, [("immediate_transfer", "=", False)]])
            if batch.picking_type_id:
                domain += [("picking_type_id", "=", batch.picking_type_id.id)]
            batch.allowed_picking_ids = self.env["stock.picking"].search(domain)
