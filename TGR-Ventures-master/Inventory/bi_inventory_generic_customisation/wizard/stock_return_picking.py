from odoo import models


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _create_returns(self):
        res = super(StockReturnPicking, self)._create_returns()
        ctx = self._context
        if "return_picking" in ctx and not isinstance(res, bool):
            new_picking_id = res[0]
            new_picking = self.env["stock.picking"].browse(new_picking_id)
            self.picking_id.write({"state": "return"})
            transfer = self.env["stock.immediate.transfer"].create(
                {
                    "pick_ids": [(4, new_picking.id)],
                    "immediate_transfer_line_ids": [(0, 0, {"to_immediate": True, "picking_id": new_picking.id})],
                }
            )
            transfer.with_context(button_validate_picking_ids=new_picking.id).process()
        return res
