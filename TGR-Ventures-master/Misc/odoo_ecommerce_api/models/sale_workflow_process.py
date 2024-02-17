from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleWorkflowProcess(models.Model):
    _inherit = "sale.workflow.process.ept"

    default_generic_so_workflow = fields.Boolean(
        "Default Generic SO Workflow", help="Default Workflow for Generic API related sale orders"
    )
    is_dropshipping_workflow = fields.Boolean("Is Dropshipping Workflow")
    is_drop_shipping_workflow_new = fields.Boolean("Is Dropshipping Workflow New")

    @api.constrains("default_generic_so_workflow")
    def _constrains_default_generic_so_workflow(self):
        """
        @private - Check for another default generic sale order workflow is enabled, Otherwise break the operation
        """
        if self.default_generic_so_workflow and self.search_count(
            [("id", "!=", self.id), ("default_generic_so_workflow", "=", True)]
        ):
            raise UserError(_("Another workflow found as default generic so workflow. You need to disable it first."))
