from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    stamp_shipping_charge_ids = fields.One2many("stamp.shipping.charge", "sale_order_id", string="Stamp Rate Matrix")
    stamp_shipping_charge_id = fields.Many2one(
        "stamp.shipping.charge",
        string="Stamp Service",
        help="This Method Is Use Full For Generating The Label",
        copy=False,
    )

    # def set_delivery_line(self, carrier, amount):
    #     # Remove delivery products from the sales order
    #     self._remove_delivery_line()
    #     for order in self:
    #         order._create_delivery_line(carrier, amount)
    #     return True
