from odoo import fields, models


class StockImmediateTransferAssignee(models.TransientModel):
    _inherit = "stock.immediate.transfer.line"

    assignee_id = fields.Many2one("res.users", string="Assignee")


class MoveStockAssignee(models.TransientModel):
    _inherit = "stock.immediate.transfer"

    def process(self):
        for each in self.pick_ids:
            lines = self.immediate_transfer_line_ids.filtered(lambda x: x.picking_id == each)
            if lines.assignee_id:
                each.assignee_id = lines.assignee_id.id
        return super(MoveStockAssignee, self).process()
