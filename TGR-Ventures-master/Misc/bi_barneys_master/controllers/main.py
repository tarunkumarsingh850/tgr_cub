import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class BarneysAPI(http.Controller):

    # send barney pricelist
    @http.route("/barneys_sales_pricelist", type="json", auth="public", methods=["GET"], csrf=False)
    def barneys_sales_pricelist(self, **args):
        request.jsonrequest
        data = []
        pricelist_lines = request.env["barneys.master"].sudo().search([])
        for line in pricelist_lines:
            data.append(
                {
                    "sku": line.odoo_sku,
                    "price": line.selling_price,
                }
            )
        return json.dumps(data)
