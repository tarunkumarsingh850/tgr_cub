from odoo import models, fields, api
import requests
import json


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _description = "Stock Picking"

    is_send_barney_shipment_information = fields.Boolean(
        "Is Send Barney Shipment Information", default=False, copy=False
    )
    is_barneys_dropshipping = fields.Boolean(string="Is Barneys Dropshipping")

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        log_book = self.env["common.log.book.ept"].search([("is_data_import_log_book", "=", True)], limit=1)
        if not log_book:
            log_book = self.env["common.log.book.ept"].create({"is_data_import_log_book": True})
        for picking in self:
            barney_orders = self.env["sale.order"].search([("is_barneys_dropshipping", "=", True)])
            barney_order = barney_orders.filtered(lambda b_order: picking in b_order.picking_ids)
            if barney_order and not picking.is_send_barney_shipment_information:
                data_body = {
                    "order_number": barney_order.name,
                }
                if picking.state == "done":
                    data_body.update({"status": "shipped", "tracking_reference": picking.carrier_tracking_ref})
                elif picking.state == "cancel":
                    data_body.update({"status": "cancelled", "cancel_reason": barney_order.cancel_reason})
                else:
                    data_body.update({"status": "waiting"})
                api_url = "https://www.barneysfarm.us/Odoo_Api/orderStatus.php"
                header = {"Content-Type": "application/json"}
                response = requests.post(api_url, json.dumps(data_body), header)
                if picking.state in ["done", "cancel"] and response.status_code in [200]:
                    picking.is_send_barney_shipment_information = True
                log_book.write(
                    {
                        "log_lines": [
                            (
                                0,
                                0,
                                {
                                    "message": response.text,
                                    "api_url": api_url,
                                    "api_data_sent": json.dumps(data_body),
                                },
                            )
                        ]
                    }
                )
        return res

    def send_barney_shipment_cron(self):
        log_book = self.env["common.log.book.ept"].search([("is_data_import_log_book", "=", True)], limit=1)
        if not log_book:
            log_book = self.env["common.log.book.ept"].create({"is_data_import_log_book": True})
        barney_orders = self.env["sale.order"].search([("is_barneys_dropshipping", "=", True)])
        for barney_order in barney_orders:
            b_pickings = barney_order.picking_ids
            for b_pick in b_pickings:
                if not b_pick.is_send_barney_shipment_information:
                    data_body = {
                        "order_number": barney_order.name,
                    }
                    if b_pick.state == "done":
                        data_body.update({"status": "shipped", "tracking_reference": b_pick.carrier_tracking_ref})
                    elif b_pick.state == "cancel":
                        data_body.update({"status": "cancelled", "cancel_reason": barney_order.cancel_reason})
                    else:
                        data_body.update({"status": "waiting"})
                    api_url = "https://www.barneysfarm.us/Odoo_Api/orderStatus.php"
                    header = {"Content-Type": "application/json"}
                    response = requests.post(api_url, data_body, header)
                    if b_pick.state in ["done", "cancel"] and response.status_code in [200]:
                        b_pick.is_send_barney_shipment_information = True
                    log_book.write(
                        {
                            "log_lines": [
                                (
                                    0,
                                    0,
                                    {
                                        "message": response.text,
                                        "api_url": api_url,
                                        "api_data_sent": json.dumps(data_body),
                                    },
                                )
                            ]
                        }
                    )

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        if (
            res.partner_id
            and res.partner_id.parent_id
            and res.partner_id.parent_id.customer_class_id
            and res.partner_id.parent_id.customer_class_id.is_barneys_customer
        ):
            carrier = self.env["delivery.carrier"].search(
                [("company_id", "=", res.company_id.id), ("is_barneys_delivery", "=", True)], limit=1
            )
            res.carrier_id = carrier.id if carrier else False
        return res
