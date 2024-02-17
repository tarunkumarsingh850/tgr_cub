import json
import logging

from odoo import http
from odoo.http import request

from odoo.addons.odoo_auth2.controllers.auth2_authentication import validate_token

_logger = logging.getLogger(__name__)


class CommonEcommerceAPI(http.Controller):
    @validate_token
    @http.route("/api/process_odoo_sale_order", type="json", auth="public", methods=["GET", "POST"], csrf=False)
    def process_odoo_sale_order(self, **kwargs):
        """
        Process the sale order with data coming through the API
        """
        try:
            data = request.jsonrequest
            _logger.info(f"Received data: {data}")
            if data:
                _logger.info("Creating sale order with received data")
                status = request.env["sale.order"].sudo().create_order_ecommerce_sale_order(data)
            else:
                status = {"error": "JSON body is empty", "error_code": False}
        except Exception as e:
            status = {"error": e, "error_code": False}
        _logger.info(status)
        return json.dumps(status)

    # send common stock for the requested warehouse/location using dropshipping_code
    @http.route("/common_stock_update", type="json", auth="public", methods=["GET"], csrf=False)
    def common_stock_update(self, **args):
        received_data = request.jsonrequest
        data = []
        if "warehouse_code" not in received_data.keys():
            return json.dumps({"error": "Warehouse code not found in request."})
        breeder_id = request.env["product.breeder"].sudo().search([("magento_id", "=", "1516")], limit=1)
        product_ids = (
            request.env["product.product"]
            .sudo()
            .search([("product_tmpl_id.product_breeder_id", "=", breeder_id.id), ("active", "=", True)])
        )
        warehouse = (
            request.env["stock.warehouse"]
            .sudo()
            .search([("dropshipping_code", "=", received_data.get("warehouse_code"))], limit=1)
        )
        required_location = warehouse.lot_stock_id
        for product in product_ids:
            stock = product.with_context(location=required_location.id).free_qty
            data.append(
                {
                    "sku": product.default_code,
                    "quantity": stock,
                }
            )
        return json.dumps(data)

    @http.route("/api/order_shipment_track", type="json", auth="public", methods=["GET", "POST"], csrf=False)
    def get_order_shipment_tracking(self, **kwargs):
        """
        Process the sale order with data coming through the API
        """
        try:
            data = request.jsonrequest
            _logger.info(f"Received data: {data}")
            if data:
                _logger.info("Creating sale order with received data")
                status = request.env["sale.order"].sudo().get_order_shipment_tracking_data(data)
            else:
                status = {"error": "JSON body is empty", "error_code": False}
        except Exception as e:
            status = {"error": e, "error_code": False}
        _logger.info(status)
        return json.dumps(status)
