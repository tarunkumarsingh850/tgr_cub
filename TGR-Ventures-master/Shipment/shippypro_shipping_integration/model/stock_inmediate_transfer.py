# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockImmediateTransferCarrier(models.TransientModel):
    _inherit = "stock.immediate.transfer.line"

    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")


class MoveStockWizard(models.TransientModel):
    _inherit = "stock.immediate.transfer"

    def process(self):
        for each in self.pick_ids:
            lines = self.immediate_transfer_line_ids.filtered(lambda x: x.picking_id == each)
            if lines.carrier_id:
                each.carrier_id = lines.carrier_id.id
            # else:
            #     raise UserError(_("Please Select Carrier"))
        return super(MoveStockWizard, self).process()
