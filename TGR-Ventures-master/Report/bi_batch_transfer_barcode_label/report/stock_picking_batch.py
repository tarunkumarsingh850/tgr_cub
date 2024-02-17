from odoo import models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    def print_zpl_barcode(self):
        return self.env.ref("bi_batch_transfer_barcode_label.batch_transfer_barcode_label_action").report_action(
            self, config=False
        )
