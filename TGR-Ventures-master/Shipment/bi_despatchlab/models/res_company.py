from odoo import fields, models, _
import requests
import json
import logging
from odoo.exceptions import ValidationError
from requests.auth import HTTPBasicAuth

_logger = logging.getLogger("despatchlab")


class ResCompanydespatch(models.Model):
    _inherit = "res.company"

    despatch_api_key = fields.Char(string="despatch lab API KEY")
    despatch_api_url = fields.Char(string="despatch lab API URL", default="https://despatchlab.com")
    despatchlab_warehouse_id = fields.Many2one("stock.warehouse", string="Despatchlab Warehouse")
    despatchlab_partner_ids = fields.Many2many("res.partner", string="Despatchlab Partners")
    diamond_logistics_customer_id = fields.Char("Diamond Logistics Customer ID")
    diamond_logistics_feature_id = fields.Char("Diamond Logistics Feature ID")
    diamond_logistics_service_type = fields.Char("Diamond Logistics Service Type")
    despatchlab_username = fields.Char("Username")
    despatchlab_password = fields.Char("Password")

    def import_carrier_from_despatch(self):
        """
        :returns this method import all carrier from despatch lab
        """
        request_data = {"Method": "GetCarriers", "Params": {}}
        headers = {"Content-Type": "application/json"}
        try:
            _logger.info(">>> sending get request to {}".format(self.despatch_api_url))
            response_data = requests.post(
                url=self.despatch_api_url,
                auth=HTTPBasicAuth(username=self.despatch_api_key, password=""),
                headers=headers,
                data=json.dumps(request_data),
            )
            if response_data.status_code in [200]:
                _logger.info(">>> get successfully response from {}".format(self.despatch_api_url))
                _logger.info(">>>> Response Data {}".format(response_data.json()))
                response_data = response_data.json()
                carriers = response_data.get("Carriers")
                if carriers:
                    for key, values in list(carriers.items()):
                        for carrier_values in values:
                            carrier_id = self.env["despatchlab.carrier"].search(
                                [("carrier_id", "=", carrier_values.get("CarrierID"))]
                            )
                            if not carrier_id:
                                vals = {
                                    "name": key,
                                    "carrier_label": carrier_values.get("Label"),
                                    "carrier_id": carrier_values.get("CarrierID"),
                                    "carrier_service": carrier_values.get("CarrierService"),
                                }
                                self.env["despatchlab.carrier"].create(vals)
                                _logger.info(
                                    "Successfully Create Carrier Into Odoo {}".format(carrier_values.get("Label"))
                                )
                            else:
                                _logger.info("Carrier Already Exist into Odoo")
                else:
                    raise ValidationError(_("Carrier Not Found Into Response \n {}").format(response_data))
            else:
                raise ValidationError(
                    _("get some error from {0} \n response data {1}").format(
                        self.despatch_api_url, response_data.content
                    )
                )
        except Exception as error:
            raise ValidationError(error)
