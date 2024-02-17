from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    correos_log = fields.Binary(
        string="Correos Logo",
    )
    canal_de_pre_registro = fields.Char(
        string="Canal de pre-registro",
    )
    correos_barcode = fields.Char(
        string="Correos Barcode",
    )

    correos_seq = fields.Integer(
        string="Correos Sequence",
    )
