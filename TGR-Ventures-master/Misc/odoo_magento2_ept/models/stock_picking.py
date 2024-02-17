# See LICENSE file for full copyright and licensing details.
"""
Describes methods for Export shipment information.
"""
import logging
import json
import requests
from odoo import models, fields, _, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta

_logger = logging.getLogger("MagentoEPT")


class StockPicking(models.Model):
    """
    Describes methods for Export shipment information.
    """

    _inherit = "stock.picking"
    _description = "Stock Picking"

    def _get_last_delivery_date(self):
        """Get the last date of delivery"""

        last_day = self.env["ir.config_parameter"].sudo().get_param("odoo_magento2_ept.delivery_last_day")
        if last_day:
            last_day = int(last_day)
            last_delivery_date = datetime.now() + timedelta(last_day)
        else:
            last_delivery_date = False
        return last_delivery_date

    is_magento_picking = fields.Boolean(
        string="Magento Picking?", help="If checked, It is Magento Picking", track_visibility="always"
    )
    related_backorder_ids = fields.One2many(
        comodel_name="stock.picking",
        inverse_name="backorder_id",
        string="Related backorders",
        help="This field relocates related backorders",
    )
    magento_website_id = fields.Many2one(
        compute="_compute_set_magento_info",
        comodel_name="magento.website",
        readonly=True,
        string="Website",
        help="Magento Websites",
        track_visibility="always",
        store=True,
    )
    storeview_id = fields.Many2one(
        compute="_compute_set_magento_info",
        comodel_name="magento.storeview",
        readonly=True,
        string="Storeview",
        help="Magento Store Views",
        track_visibility="always",
    )

    magento_status = fields.Char(string="Magento Status", compute="_compute_set_magento_info", store=True)

    magento_payment_code = fields.Char(string="Magento Payment Code", compute="_compute_payment_code")

    is_exported_to_magento = fields.Boolean(
        string="Exported to Magento?", help="If checked, Picking is exported to Magento", track_visibility="always"
    )
    magento_instance_id = fields.Many2one(
        comodel_name="magento.instance",
        string="Instance",
        help="This field relocates magento instance",
        track_visibility="always",
    )
    magento_shipping_id = fields.Char(
        string="Magento Shipping Ids", help="Magento Shipping Ids", track_visibility="always"
    )
    max_no_of_attempts = fields.Integer(string="Max NO. of attempts", default=0, track_visibility="always")
    magento_message = fields.Char(string="Picking Message", track_visibility="always")
    magento_inventory_source = fields.Many2one(
        comodel_name="magento.inventory.locations",
        string="Magento Inventory Sources",
        domain="[('magento_instance_id', '=', magento_instance_id)]",
        track_visibility="always",
    )
    is_msi_enabled = fields.Boolean(
        related="magento_instance_id.is_multi_warehouse_in_magento", track_visibility="always"
    )
    is_shipment_exportable = fields.Boolean(
        string="Is Shipment exportable", compute="_compute_shipment_exportable", store=False, track_visibility="always"
    )
    last_delivery_date = fields.Date("Last Delivery Date", default=_get_last_delivery_date, track_visibility="always")
    invoice_id = fields.Many2one("account.move", string="Invoice", copy=False)

    is_resend_order = fields.Boolean(
        string="Resend Order",
    )
    resend_reason = fields.Char("Resend Reason")

    @api.depends("sale_id")
    def _compute_payment_code(self):
        for picking in self:
            if picking.sale_id:
                picking.magento_payment_code = picking.sale_id.magento_payment_code
            else:
                picking.magento_payment_code = ""

    def _compute_shipment_exportable(self):
        """
        set is_shipment_exportable true or false based on some condition
        :return:
        """
        for picking in self:
            picking.is_shipment_exportable = False
            if picking.magento_instance_id and picking.picking_type_id.code == "outgoing":
                picking.is_shipment_exportable = True

    @api.depends("sale_id")
    def _compute_set_magento_info(self):
        """
        Computes Magento Information
        :return:
        """
        for record in self:
            if record.sale_id.magento_order_id:
                record.magento_website_id = record.sale_id.magento_website_id
                record.storeview_id = record.sale_id.store_id
                record.magento_status = record.sale_id.magento_status
                # record.note = record.sale_id.magento_billing_address
            else:
                record.storeview_id = False
                record.magento_website_id = False
                record.magento_status = False
                # record.note = record.note and record.note or False
#Disable the address to notes

    def get_export_ship_values(self, raise_error):
        """
        export shipment values create with item details.
        param: wizard - open this values export shipment (t/f).
        return : export shipment dict.
        """
        if self.carrier_id and not self.carrier_id.magento_carrier_code and not raise_error:
            message = (
                "You are trying to Export Shipment Information"
                "\nBut Still, you didn't set the Magento "
                "Carrier Code for '{}' Delivery Method".format(self.carrier_id.name)
            )
            raise UserError(message)
        items = self.__prepare_export_shipment_items()
        tracks = self.get_magento_tracking_number()
        values = {"items": items, "tracks": tracks or []}
        if self.is_msi_enabled and self.magento_inventory_source:
            values.update(
                {
                    "arguments": {
                        "extension_attributes": {"source_code": self.magento_inventory_source.magento_location_code}
                    }
                }
            )
        return values

    def __prepare_export_shipment_items(self):
        """
        This method are used to prepare shipment items values.
        :return: list(dict(orderItemId, qty))
        """
        items = []
        for move in self.move_lines:
            item_id = move.sale_line_id.magento_sale_order_line_ref
            if move.sale_line_id and item_id:
                # order_item_id = move.sale_line_id.magento_sale_order_line_ref
                # only ship those qty with is done in picking. Not for whole order qty done
                items.append({"orderItemId": item_id, "qty": move.quantity_done})
        return items

    def magento_send_shipment(self, raise_error=False):
        """
        This method are used to send the shipment to Magento. This is an base method and it calls
        from wizard, manual operation as well as cronjob.
        :param raise_error: If calls from manual operation then raise_error=True
        :return: Always True
        """
        for picking in self:

            if picking.is_magento_picking:
                self.env["sale.order"].search([("picking_ids", "in", picking.id)])
            values = {}
            items = []
            tracks = []
            for move in self.move_lines:
                item_id = move.sale_line_id.magento_sale_order_line_ref
                if move.sale_line_id and item_id:
                    items.append({"orderItemId": item_id, "qty": move.quantity_done})
                    tracks = []
            title = picking.carrier_id.name
            carrier_code = False
            tracks.append(
                {
                    "carrierCode": "custom",
                    "title": title,
                    "trackNumber": picking.carrier_tracking_ref,
                }
            )
            if not tracks and self.carrier_tracking_ref:
                tracks.append({"carrierCode": carrier_code, "title": title, "trackNumber": self.carrier_tracking_ref})
            values = {"items": items, "notify": True, "tracks": tracks or []}
            instance = picking.magento_instance_id
            try:
                api_url = f"{instance.magento_url}/rest/V1/order/{picking.sale_id.magento_order_id}/ship/"
                # response = req(instance, api_url, "POST", values)
                response = requests.post(
                    api_url, data=json.dumps(values), headers=self.get_headers(instance.access_token)
                )
            except Exception as error:
                _logger.error(error)
                return self._handle_magento_shipment_exception(instance, picking)
            if response.status_code in [200, 202]:
                picking.write({"is_exported_to_magento": True})
            picking.write({"magento_message": response.text})
        return True

    def get_headers(self, token):
        return {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "My User Agent 1.0",
            "Authorization": "Bearer {}".format(token),
        }

    def _handle_magento_shipment_exception(self, instance, picking):
        """
        This method used to handle shipment response. Based on the response we will update the
        attempts and shipment id in picking record.
        :param instance: magento.instance object
        :param picking: stock.picking object
        :return: Always False due to this method calls from exception
        """
        model_id = self.env["common.log.lines.ept"].get_model_id(self._inherit)
        log = self.env["common.log.book.ept"].create_common_log_book(
            "import", "magento_instance_id", instance, model_id, "magento_ept"
        )
        order_name = picking.sale_id.name
        if picking.max_no_of_attempts == 2:
            note = f"""
            Attention {self.name} Export Shipment is processed 3 times and it failed. \n
            You need to process it manually.
            """
            self.env["magento.instance"].create_activity(
                model_name=self._name, res_id=picking.id, message=note, summary=picking.name, instance=instance
            )
        picking.write(
            {
                "max_no_of_attempts": picking.max_no_of_attempts + 1,
                "magento_message": _(
                    "The request could not be satisfied while export this Shipment." "\nPlease check Process log {}"
                ).format(log.name),
            }
        )
        message = _(
            "The request could not be satisfied and shipment couldn't be "
            "created in Magento for "
            "Sale Order : {} & Picking : {} due to any of the following reasons.\n"
            "1. A picking can't be created when an order has a status of "
            "'On Hold/Canceled/Closed'\n"
            "2. A picking can't be created without products. "
            "Add products and try again.\n"
            "3. The shipment information has not been exported due "
            "to either missing carrier or"
            " tracking number details.\n"
            "4. In case you are using Magento multi-inventory sources, "
            "ensure that you have selected the appropriate warehouse location for "
            "the shipment in Odoo. "
            "The warehouse location must be listed as one of the inventory sources "
            "set up in Magento for the product. "
            "Please go to Magento2 Odoo Connector > Configuration > "
            "Magento Inventory location > Select Magento location name > "
            "set Export Shipment location\n"
            "The order does not allow an shipment to be created"
        ).format(order_name, picking.name)
        log.write(
            {
                "log_lines": [
                    (
                        0,
                        0,
                        {
                            "message": message,
                            "order_ref": order_name,
                        },
                    )
                ]
            }
        )
        return False

    def search_magento_pickings(self, instance):
        """
        This method are used to search the picking which are exportable. We only consider the
        OUTGOING pickings to be exported and if it already attempted more than 3 times then we
        will not export it again when cronjob runs.
        :param instance: magento.instance object
        :return: stock.picking records
        """
        return self.search(
            [
                ("is_exported_to_magento", "=", False),
                ("state", "in", ["done"]),
                ("magento_instance_id", "=", instance.id),
                ("max_no_of_attempts", "<=", 3),
                ("picking_type_id.code", "=", "outgoing"),
            ]
        )

    def get_magento_tracking_number(self):
        """
        Add new Tracking Number for Picking.
        :return: list(tracking)
        """
        tracks = []
        carrier_code = self.carrier_id.magento_carrier_code
        title = self.carrier_id.magento_carrier.magento_carrier_title
        for package in self.package_ids:
            tracks.append(
                {
                    "carrierCode": carrier_code,
                    "title": title,
                    "trackNumber": package.tracking_no or self.carrier_tracking_ref,
                }
            )
        if not tracks and self.carrier_tracking_ref:
            tracks.append({"carrierCode": carrier_code, "title": title, "trackNumber": self.carrier_tracking_ref})
        return tracks

    def export_magento_shipment(self):
        """
        This method calls from manual operation button provided in stock.picking.
        :return:
        """
        return self.magento_send_shipment(raise_error=True)

    def auto_cancel_delivery_orders(self):
        """
        This method used to cancel the delivery order and sale order if there is no payment against them.
        This method is called from cron job.
        """
        # pickings = self.env["stock.picking"].search(
        #     [("last_delivery_date", "<=", date.today()), ("state", "not in", ["cancel", "done"])]
        # )
        pickings = self.env["stock.picking"].search(
            [("state", "not in", ["cancel", "done"]), ("sale_id", "!=", False), ("last_delivery_date", "!=", False)],
            limit=1,
        )
        today = datetime.today()
        for each in pickings:
            # sale_order = self.env["sale.order"].search([("picking_ids", "in", each.id)])
            # if sale_order:
            # if len(sale_order.mapped("invoice_ids").filtered(lambda x: x.amount_total == x.amount_residual)) == 0:
            #     each.action_cancel()
            #     sale_order.action_cancel()
            #     sale_order.cancel_order_in_magento()
            if (
                each.sale_id
                and each.sale_id.magento_payment_method_id
                and each.sale_id.magento_payment_method_id.is_cancel_delivery_order
                and each.last_delivery_date
            ):
                days = each.sale_id.magento_payment_method_id.days_before_cancel_delivery_order
                days_ago = (today - timedelta(days=days)).date()
                if (
                    each.last_delivery_date <= days_ago
                    and len(each.sale_id.mapped("invoice_ids").filtered(lambda x: x.amount_total == x.amount_residual))
                    == 0
                ):
                    each.action_cancel()
                    each.sale_id.action_cancel()
                    each.sale_id.cancel_order_in_magento()

    def button_validate(self):
        if self.env.context.get("skip_immediate", False):
            pickings_to_do = self.env["stock.picking"]
            for each in self:
                if each.is_magento_picking:
                    if (
                        each.is_credit_customer
                        or each.payment_status == "paid"
                        or each.payment_status == "paid_and_batched"
                        or each.is_proof_of_payment_received
                        or each.sale_id.is_resend_order
                    ):
                        pickings_to_do |= each
                    else:
                        raise UserError(_(f"Delivery {each.name} Can't Validate Without payment"))
                else:
                    pickings_to_do |= each
            if pickings_to_do:
                pickings_to_do.validate_invoice_with_picking_date()
        result = super(StockPicking, self).button_validate()
        return result

    def validate_invoice_with_picking_date(self):
        for picking in self:
            if picking.sale_id and not picking.is_resend_order:
                if picking.sale_id.invoice_ids.filtered(
                    lambda inv: inv.move_type == "out_invoice" and inv.state in ["draft", "posted"]
                ):
                    invoice = picking.sale_id.invoice_ids[0]
                    if invoice.state == "draft":
                        invoice.invoice_date = fields.Datetime.now()
                        invoice.date = fields.Datetime.now()
                        invoice._compute_picking_details()
                        invoice.with_context(is_auto_workflow=True).action_post()
                else:
                    invoice = picking.sale_id._create_invoices()
                    invoice.invoice_date = fields.Datetime.now()
                    invoice.date = fields.Datetime.now()
                    invoice.with_context(is_auto_workflow=True).action_post()
                picking.invoice_id = invoice.id

    def open_invoice(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Invoice"),
            "res_model": "account.move",
            "res_id": self.invoice_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_cancel(self):
        for rec in self:
            if rec.state in ["draft", "assigned", "waiting", "confirmed"]:
                rec.mapped("move_lines")._action_cancel()
                rec.write({"is_locked": True})
                rec.filtered(lambda x: not x.move_lines).state = "cancel"
                return True
