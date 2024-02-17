from odoo import fields, models


class AssignAssigneeWizard(models.TransientModel):
    _name = "assign.assignee.wizard"

    assignee_id = fields.Many2one("res.users", string="Picker")

    def assign_assignee(self):
        stock_picking = self.env["stock.picking"].browse(self._context.get("active_ids", []))
        for each in stock_picking:
            each.user_id = self.assignee_id.id
