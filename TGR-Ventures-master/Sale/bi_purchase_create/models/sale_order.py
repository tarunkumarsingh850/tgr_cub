from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_ids = fields.Many2many("purchase.order", string="Purchase")

    @api.model
    def create_purchase_wizard(self, selected_ids):
        res_user_security = self.env["res.users"].search([("id", "=", self._uid)])
        flag = False
        flag = res_user_security.has_group("bi_purchase_create.group_user")
        if flag is False:
            return {"error": True}
        orderline_sudo = self.env["sale.order.line"].sudo()
        order_lines = orderline_sudo.browse(selected_ids)
        # order_id = order_lines.mapped("order_id")
        product_ids = []
        for line in order_lines:
            product_ids.append(
                (
                    0,
                    0,
                    {
                        "product_id": line.product_id.id,
                        "vendor_id": line.vendor_id.id,
                        "uom_id": line.product_uom.id,
                        "description_name": line.name,
                        "quantity": line.product_uom_qty,
                        "unit_price": line.price_unit,
                        "price_subtotal": line.price_subtotal,
                        "sale_id": line.order_id.id,
                    },
                )
            )
        return {"line_ids": product_ids}


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    vendor_id = fields.Many2one("res.partner", string="Vendor")
