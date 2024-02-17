from odoo import fields, models


class ParcelDetails(models.Model):
    _inherit = "stock.picking"

    parcel_length = fields.Float("Length", track_visibility="always")
    parcel_width = fields.Float("Width", track_visibility="always")
    parcel_height = fields.Float("Height", track_visibility="always")
    parcel_weight = fields.Float("Weight", track_visibility="always")
    no_of_packages = fields.Float("No. Of Packages", default=1.0, track_visibility="always")
