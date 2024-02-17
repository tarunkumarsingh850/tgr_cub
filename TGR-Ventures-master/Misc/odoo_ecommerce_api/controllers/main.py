import json
import logging

from odoo import http
from odoo.http import request

from odoo.addons.odoo_auth2.controllers.auth2_authentication import validate_token

_logger = logging.getLogger(__name__)


class OdooEcommerceAPI(http.Controller):
    @validate_token
    @http.route("/api/process_sale_order", type="json", auth="public", methods=["GET", "POST"], csrf=False)
    def process_sale_order(self, **kwargs):
        """
        Process the sale order with data coming through the API
        """
        try:
            data = request.jsonrequest
            _logger.info(f"Received data: {data}")
            if data:
                _logger.info("Creating sale order with received data")
                status = request.env["sale.order"].sudo().create_ecommerce_sale_order(data)
            else:
                status = {"error": "JSON body is empty", "error_code": False}
        except Exception as e:
            status = {"error": e, "error_code": False}
        _logger.info(status)
        return json.dumps(status)

    @http.route("/api/dropship_shipment_track", type="json", auth="public", methods=["GET", "POST"], csrf=False)
    def get_sale_order_shipment_tracking(self, **kwargs):
        """
        Process the sale order with data coming through the API
        """
        try:
            data = request.jsonrequest
            _logger.info(f"Received data: {data}")
            if data:
                _logger.info("Creating sale order with received data")
                status = request.env["sale.order"].sudo().get_shipment_tracking_data(data)
            else:
                status = {"error": "JSON body is empty", "error_code": False}
        except Exception as e:
            status = {"error": e, "error_code": False}
        _logger.info(status)
        return json.dumps(status)

    # send fastbuds stock for the requested warehouse/location using dropshipping_code
    @http.route("/get_brand_stock", type="json", auth="public", methods=["GET"], csrf=False)
    def get_brand_stock(self, **args):
        received_data = request.jsonrequest
        data = []
        if "warehouse_code" not in received_data.keys():
            return json.dumps({"error": "Warehouse code not found in request."})
        if "brand_code" not in received_data.keys():
            return json.dumps({"error": "Brand code not found in request."})
        breeder_id = (
            request.env["product.breeder"]
            .sudo()
            .search([("magento_id", "=", received_data.get("brand_code"))], limit=1)
        )
        if not breeder_id:
            return json.dumps({"error": "Brand not found."})
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

    # send barney pricelist
    @http.route("/dropshipping_sales_pricelist", type="json", auth="public", methods=["GET"], csrf=False)
    def dropshipping_sales_pricelist(self, **args):
        received_data = request.jsonrequest
        data = []
        if "customer_ref" not in received_data.keys():
            return json.dumps({"error": "Customer reference not found in request."})
        customer_class = request.env["customer.class"].sudo().search([("is_dropshipping", "=", True)], limit=1)
        customer = (
            request.env["res.partner"]
            .sudo()
            .search(
                [("ref", "=", received_data.get("customer_ref", False)), ("customer_class_id", "=", customer_class.id)],
                limit=1,
            )
        )
        if not customer:
            return json.dumps({"error": "Customer not found."})
        if not customer.property_product_pricelist:
            return json.dumps({"error": f"Pricelist not found for {customer.name}."})
        pricelist_property = (
            request.env["ir.property"]
            .sudo()
            .search(
                [
                    ("company_id", "=", 11),  # tgrventure corp usa
                    ("name", "=", "property_product_pricelist"),
                    ("res_id", "=", f"{customer._name},{customer.id}"),
                    ("type", "=", "many2one"),
                ]
            )
        )
        pricelist = (
            request.env["product.pricelist"].sudo().browse(int(pricelist_property.value_reference.split(",")[-1]))
        )
        for line in pricelist.item_ids:
            data.append(
                {
                    "sku": line.product_tmpl_id.default_code,
                    "price": line.fixed_price,
                }
            )
        return json.dumps(data)
