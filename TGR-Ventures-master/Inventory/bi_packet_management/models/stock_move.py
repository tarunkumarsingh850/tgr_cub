from odoo import fields, models


class StockMovePacket(models.Model):
    _inherit = "stock.move"

    packet_id = fields.Many2one("packet.management", string="Packet")
