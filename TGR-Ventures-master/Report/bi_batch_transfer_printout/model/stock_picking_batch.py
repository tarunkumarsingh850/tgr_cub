from odoo import fields, models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    batch_picking_description = fields.Char("Batch Description")
    boolean_status_validate = fields.Boolean(default=False, compute="_compute_status_validate")

    def _compute_status_validate(self):
        if self.picking_ids:
            self.boolean_status_validate = True
            for line in self.picking_ids:
                if line.state != "done":
                    self.boolean_status_validate = False
            if self.boolean_status_validate is True:
                self.write(
                    {
                        "state": "done",
                    }
                )
