from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _description = "Stock Picking"

    def button_validate(self):
        res = super(StockPicking, self).button_validate()

        if ("skip_backorder" not in self.env.context.keys()) and self.picking_type_id.code == "outgoing":
            for rec in self.move_ids_without_package:
                if rec.quantity_done > 0:

                    po_ids = (
                        self.env["purchase.order"]
                        .search(
                            [
                                ("is_consignment_used", "=", False),
                                ("is_consignment_order", "=", True),
                                ("state", "=", "purchase"),
                            ],
                            order="date_order ASC",
                        )
                        .filtered(
                            lambda po: any(
                                line.product_id == rec.product_id
                                and line.quantity_sold < line.qty_received
                                and line.warehouse_dest_id == rec.warehouse_id
                                for line in po.order_line
                            )
                        )
                    )
                    stop_iteration = False
                    qty_left = rec.quantity_done
                    for po_id in po_ids:
                        if not stop_iteration:
                            for order_line in po_id.order_line:
                                if rec.product_id == order_line.product_id:
                                    balance = qty_left + order_line.quantity_sold - order_line.qty_received
                                    if balance > 0:
                                        order_line.quantity_sold += qty_left - balance
                                        rec.sale_line_id.consignment_ids = [(4, po_id.id)]
                                        lines = [
                                            (
                                                0,
                                                0,
                                                {"so_line_id": rec.sale_line_id.id, "so_sold_qty": qty_left - balance},
                                            )
                                        ]
                                        so_id = po_id.sudo().write({"so_line_ids": lines})
                                        qty_left = balance
                                        break
                                    elif balance <= 0:
                                        order_line.quantity_sold += qty_left
                                        rec.sale_line_id.consignment_ids = [(4, po_id.id)]
                                        lines = [(0, 0, {"so_line_id": rec.sale_line_id.id, "so_sold_qty": qty_left})]
                                        so_id = po_id.sudo().write({"so_line_ids": lines})
                                        stop_iteration = True
                                        break
        return res


class StockMove(models.Model):
    _inherit = "stock.move"
    _description = "Stock Move"
