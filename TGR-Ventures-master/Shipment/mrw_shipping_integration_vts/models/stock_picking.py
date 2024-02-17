from odoo import fields, models


class MrwShipmentNumber(models.Model):
    _inherit = "stock.picking"
    mrw_label_url = fields.Char(string="Mrw Label Url", help="Url for Generate Label")
    shipment_details = fields.Char(string="Shipment Details", help="Url For View Shipment Details")

    def retry_mrw_shipping(self):
        for picking in self:
            if picking.carrier_tracking_ref:
                res = picking.carrier_id.mrw_vts_send_shipping(picking)
                if res:
                    picking.carrier_tracking_ref = res[0]["tracking_number"]
