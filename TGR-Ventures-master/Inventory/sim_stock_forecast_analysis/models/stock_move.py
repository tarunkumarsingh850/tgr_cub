from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    date_expected2 = fields.Date(string="Expected Date", compute="_compute_date_expected2", readonly=True, store=True)

    @api.depends("date")
    def _compute_date_expected2(self):
        for move in self:
            timestamp_utc = fields.Datetime.from_string(move.date)
            timestamp_local = fields.Datetime.context_timestamp(self, timestamp=timestamp_utc)
            move.date_expected2 = fields.Date.to_string(timestamp_local)
