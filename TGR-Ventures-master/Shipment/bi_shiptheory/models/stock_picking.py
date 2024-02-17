from odoo import fields, models
from datetime import datetime, timedelta


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def get_shiptheory_scheduled_date(self):
        if self.scheduled_date:
            shiptheory_scheduled_date = self.scheduled_date + timedelta(days=1)
        else:
            shiptheory_scheduled_date = datetime.now()
        return shiptheory_scheduled_date

    shiptheory_tracking = fields.Char(
        string="Shiptheory Token",
    )
    shiptheory_scheduled_date = fields.Datetime(
        string="Shiptheory Scheduled Date",
        default=get_shiptheory_scheduled_date,
    )

    def generate_shiptheory_label(self):
        self.carrier_id.generate_shiptheory_label_using_order_id(self, self.origin, self.shiptheory_tracking)
