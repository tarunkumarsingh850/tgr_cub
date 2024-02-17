from odoo import api, models, _
from odoo.exceptions import UserError


class StockMove(models.AbstractModel):
    _name = "report.bi_purchase_receipt.report_purchase_receipt"
    _description = "StockMove"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["stock.picking"].browse(docids)
        val = []
        if docs.picking_type_code == "incoming":
            total_qty = 0
            receipt_total = 0
            for lines in docs.move_ids_without_package:
                total_qty += lines.product_uom_qty
                receipt_total += lines.purchase_line_id.price_subtotal

            values = {
                "total_qty": total_qty,
                "receipt_total": receipt_total,
            }
            val.append(values)

            return {"doc_ids": docs.ids, "doc_model": "stock.picking", "data": data, "docs": docs, "vals": val}
        else:
            raise UserError(_("Receipt cannot be printed from delivery "))
