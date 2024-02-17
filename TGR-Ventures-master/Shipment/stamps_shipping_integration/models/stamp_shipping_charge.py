from odoo import fields, models


class StampRateShippingCharge(models.Model):
    _name = "stamp.shipping.charge"
    _rec_name = "stamp_service_name"
    stamp_service_name = fields.Char(string="Stamp Shipping Service Name")
    stamp_service_rate = fields.Float(string="Stamp Shipping Charge ")
    stamp_service_delivery_date = fields.Char(string="Stamp Service Delivery Day")
    sale_order_id = fields.Many2one("sale.order", string="Sales Order")

    def set_service(self):
        self.ensure_one()
        carrier = self.sale_order_id.carrier_id
        self.sale_order_id._remove_delivery_line()
        self.sale_order_id.stamp_shipping_charge_id = self.id
        # self.sale_order_id.delivery_price = float(self.envia_total_price)
        self.sale_order_id.carrier_id = carrier.id
        self.sale_order_id.set_delivery_line(carrier, self.stamp_service_rate)
