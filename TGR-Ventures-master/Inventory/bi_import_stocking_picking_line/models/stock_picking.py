from odoo import _, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_import(self):
        return {
            "name": _("Import Lines"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "stock.import.wizard",
            "context": {"default_stock_picking_update_id": self.id},
            "target": "new",
        }
