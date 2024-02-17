from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "mail.thread", "mail.activity.mixin"]

    def _country_check_country(self):
        picking_ids = self.env["stock.picking"].search([])
        for each in picking_ids:
            if each.partner_id:
                if each.partner_id.country_id:
                    each.country_id = each.partner_id.country_id.id
                else:
                    each.country_id = False
            else:
                each.country_id = False

    reason_code_id = fields.Many2one("reason.code", string="Reason Code", track_visibility="always")
    shipping_zone_id = fields.Many2one("shipping.zone", string="Shipping Zone", track_visibility="always")
    assignee_id = fields.Many2one("res.users", string="Assignee", track_visibility="always")
    sale_boolean = fields.Boolean(
        string="sale", default=False, compute="_compute_sale_order", track_visibility="always"
    )
    country_id = fields.Many2one("res.country", string="Country", store=True, track_visibility="always")
    is_partner_carrier = fields.Boolean(string="Is Partner Carrier", default=False, track_visibility="always")
    country_group_id = fields.Many2one(
        string="Country Group",
        comodel_name="res.country.group",
        related="country_id.country_group_id",
        store=True,
        track_visibility="always",
    )
    is_hold = fields.Boolean("Hold", default=False, copy=False, track_visibility="always")
    is_cancel = fields.Boolean("Cancel", default=False, copy=False, track_visibility="always")
    reason = fields.Char("Reason", copy=False, track_visibility="always")
    hold_reason_id = fields.Many2one("hold.reason", string="Hold Reason", track_visibility="always")
    payment_status = fields.Selection(
        [
            ("not_paid", "Not Paid"),
            ("paid", "Paid"),
            ("credit", "Credit Customer"),
            ("paid_and_batched", "Processing/Batched"),
            ("paid_refund", "Refund"),
            ("unpaid_refund", "Unpaid Refund"),
        ],
        compute="_compute_payment_status",
        string="Payment Status",
        track_visibility="always",
        copy=False,
        store=True,
    )
    is_paid = fields.Boolean("is_paid", default=False, copy=False)
    is_proof_of_payment_received = fields.Boolean(
        string="Proof Of Payment Received",
    )
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier", check_company=True, track_visibility="always")
    carrier_tracking_ref = fields.Char(string="Tracking Reference", copy=False, track_visibility="always")
    sale_total_amount = fields.Float(string="Sale Total Amount", compute="_compute_sale_total")
    carrier = fields.Char(string="Carrier", compute="_compute_carrier")
    set_paid = fields.Boolean(string="Set Paid", help="add a boolean to update payment status for old orders")
    additional_notes = fields.Text(
        string="Customer Notes (Magento)",
    )
    is_sendmail = fields.Boolean(
        string="Is Sendmail",
    )
    new_priority = fields.Selection(
        string="Priority", selection=[("low", "Low"), ("medium", "Medium"), ("high", "High")]
    )
    is_credit_customer = fields.Boolean(string="Credit Customer", compute="_compute_is_credit_customer", store=True)
    sale_order_date = fields.Datetime("Sale Order Date", related="sale_id.date_order")
    stock_move_total_cost = fields.Float(
        string="Total Cost", compute="compute_stock_move_total_cost"
    )  # ar added on 12042023
    batch_state = fields.Selection(
        [
            ("no_batch", "No Batch"),
            ("draft", "Draft"),
            ("in_progress", "In progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        store=True,
        compute="_compute_batch_state",
    )
    partner_zip_code = fields.Char("Zip Code", related="partner_id.zip")
    is_send_email_notification = fields.Boolean(string="Is Send Email Notification", default=False, copy=False)
    email_notification_content = fields.Char(
        string="Email Content",
        help="This field store log note when user delete stock move " "if reserved quantity is not available.",
    )
    state = fields.Selection(selection_add=[("return", "Return"), ("processing_batched", "Processing/Batched")])
    chargeback_customer_tag = fields.Selection(
        [("charge_back_customer", "Charge Back Customer")],
        string="Charge Back Customer",
        compute="compute_charge_back_customer",
    )
    origin = fields.Char(
        "Source Document",
        index=True,
        states={"done": [("readonly", False)], "cancel": [("readonly", True)]},
        track_visibility="always",
        help="Reference of the document",
    )
    is_reship = fields.Boolean('Is Reship', defaul=False)
    fraud_score = fields.Char('Fraud Score')

    @api.depends("batch_id")
    def _compute_batch_state(self):
        for picking in self:
            if picking.batch_id:
                picking.batch_state = picking.batch_id.state
            else:
                picking.batch_state = "no_batch"

    @api.depends("move_ids_without_package.cost")
    def compute_stock_move_total_cost(self):
        for rec in self:
            if rec.move_ids_without_package:
                rec.stock_move_total_cost = sum(rec.move_ids_without_package.mapped("cost"))
            else:
                rec.stock_move_total_cost = 0

    @api.depends("partner_id")
    def _compute_is_credit_customer(self):
        for each in self:
            pass
            # if each.partner_id.is_credit_customer or each.partner_id.parent_id.is_credit_customer:
            #     each.is_credit_customer = True
            # else:
            #     each.is_credit_customer = False

    def update_cron_is_credit_customer(self):
        pickings = self.env["stock.picking"].search([("is_credit_customer", "=", False)])
        for each in pickings:
            pass
            # if each.partner_id.is_credit_customer or each.partner_id.parent_id.is_credit_customer:
            #     each.is_credit_customer = True
            # else:
            #     each.is_credit_customer = False

    def _compute_carrier(self):
        for record in self:
            if record.sale_id:
                record.carrier = record.sale_id.magento_shipping_method_id.carrier_label
            else:
                record.carrier = False

    def _compute_sale_total(self):
        for record in self:
            sale_total_amount = 0
            if record.sale_id:
                sale_total_amount = record.sale_id.amount_total
            record.sale_total_amount = sale_total_amount

    @api.depends("set_paid", "is_credit_customer", "is_resend_order", "invoice_id.payment_state", "batch_id")
    def _compute_payment_status(self):
        for each in self:
            each.payment_status = "not_paid"
            each.is_paid = False
            if each.is_resend_order:
                each.payment_status = "paid"
                each.is_paid = True
                break
            if each.invoice_id and each.invoice_id.payment_state in ["in_payment", "paid"]:
                each.payment_status = "paid"
                each.is_paid = True
            elif each.sale_id:
                payment_ids = self.env["account.payment"].search([("sale_id", "=", each.sale_id.id)])
                if payment_ids.mapped("state") == ["posted"]:
                    each.payment_status = "paid"
                    each.is_paid = True
                # elif invoice:
                #     if invoice.mapped("payment_state")[0] in ["paid", "in_payment"]:
                #         each.payment_status = "paid"
                #         each.is_paid = True
                #     else:
                #         each.payment_status = "not_paid"
                #         each.is_paid = False
                else:
                    each.payment_status = "not_paid"
                    each.is_paid = False
            if each.set_paid:
                each.payment_status = "paid"
                each.is_paid = True
            if each.state == "done" and each.carrier_tracking_ref:
                each.payment_status = "paid"
            if each.is_credit_customer:
                each.payment_status = "credit"
            if each.magento_status == 'btcpay_underpaid':
                each.payment_status = "not_paid"
            if each.sale_total_amount <= 0.00:
                each.payment_status = "paid"
            # if each.batch_id and each.payment_status == 'paid':
            #     each.payment_status = 'paid_and_batched'

    # FUNCTION TO CHANGE PAYMENT STATUS FOR OLD ORDERS
    def action_trigger_payment_status(self):
        for record in self:
            if record.sale_id and record.is_credit_customer:
                record.payment_status = "credit"

    @api.depends("name", "partner_id")
    def _compute_sale_order(self):
        for each in self:
            if each.sale_id:
                each.sale_boolean = True
            else:
                each.sale_boolean = False

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        if res.partner_id.parent_id.carrier_id:
            res.carrier_id = res.partner_id.parent_id.carrier_id.id
            res.is_partner_carrier = True
        elif res.partner_id.carrier_id:
            res.carrier_id = res.partner_id.carrier_id.id
            res.is_partner_carrier = True
        res.country_id = res.partner_id.country_id.id
        sale_id = self.env["sale.order"].search([("name", "=", res.origin)], limit=1)
        if sale_id:
            if sale_id.is_hold:
                res.is_hold = True
                res.hold_reason_id = sale_id.hold_reason_id.id
            if sale_id.fraud_score:
                res.fraud_score = sale_id.fraud_score
        return res

    @api.onchange("partner_id")
    def onchange_country_partner_id(self):
        for each in self:
            if each.partner_id:
                if each.partner_id.country_id:
                    each.country_id = each.partner_id.country_id.id

    def wizard_tracking(self):
        return {
            "name": _("Update Tracking Ref"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "tracking.reference.wizard",
            "context": {"default_stock_picking_id": self.id},
            "target": "new",
        }

    def action_update_stock_warehouse(self):
        return {
            "name": _("Switch Warehouse"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "update.warehouse.wizard",
            "context": {
                "default_stock_picking_ids": self.ids,
                "default_current_location_id": self.location_id.ids,
            },
            "target": "new",
        }

    def action_cancel_picking_order(self):
        for order in self:
            order.action_cancel()

    def action_send_shipment_mail(self):
        for record in self:
            template = self.env.ref("bi_inventory_generic_customisation.email_template_transfer")
            template.email_from = "info@tiger-one.eu"
            template.send_mail(record.id, force_send=True)
            record.is_sendmail = True

    def action_download_attachment(self):
        tab_id = []
        for picking in self:
            tab_id.append(picking.attachment_label_id.id)
        url = "/web/binary/download_documents?tab_id=%s" % tab_id
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }

    def action_cancel(self):
        res = super(StockPicking, self).action_cancel()
        for picking in self:
            sale_order = self.env["sale.order"].search([("picking_ids", "in", picking.ids)])
            inv = sale_order.invoice_ids.filtered(lambda inv: inv.state == "draft")
            inv.button_cancel()
            sale_order.write({"state": "cancel", "show_update_pricelist": False})
        return res

    def send_email_notification(self):
        for rec in self:
            email_template = self.env.ref("bi_inventory_generic_customisation.email_template_refund_notification")
            if email_template:
                email_template.send_mail(rec.id, force_send=True)
                rec.is_send_email_notification = False
                rec.email_notification_content = ""
      

    # def button_validate(self):
    #     for res in self:
    #         if not res.carrier_tracking_ref and not 'is_tracking_ref_msg' in self.env.context:
    #             if res.picking_type_id.code == 'outgoing':
    #                 view = self.env.ref("bi_inventory_generic_customisation.shock_message_wizard_form")
    #                 context = dict(self._context or {})

    #                 context["message"] = "No Value in Tracking Reference"
    #                 return {
    #                         "name": "Alert Message",
    #                         "type": "ir.actions.act_window",
    #                         "view_type": "form",
    #                         "view_mode": "form",
    #                         "res_model": "shock.message.wizard",
    #                         "views": [(view.id, "form")],
    #                         "view_id": view.id,
    #                         "target": "new",
    #                         "context": context,
    #                 }
    #         return super(StockPicking, self).button_validate()

    def button_payment_status_refund(self):
        for rec in self:
            if rec.payment_status == "not_paid":
                rec.payment_status = "unpaid_refund"
            if rec.payment_status == "paid":
                rec.payment_status = "paid_refund"

    @api.depends("state")
    def _compute_show_validate(self):
        """
        inherit function if state is processing_batched then show_validate should be True.
        Returns:

        """
        res = super(StockPicking, self)._compute_show_validate()
        for picking in self:
            if picking.state == "processing_batched":
                picking.show_validate = True
        return res

    @api.depends("partner_id")
    def compute_charge_back_customer(self):
        for picking in self:
            picking.chargeback_customer_tag = ""
            if picking.partner_id and picking.partner_id.usa_charge_back:
                picking.chargeback_customer_tag = "charge_back_customer"

    def duplicate_picking(self):
        new_picking_id = self.copy()
        new_picking_id.write({'origin': 'RESHIP - ' + self.origin, 
                              'is_reship' : True,
                              'sale_id': self.sale_id.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(self.env.ref('stock.view_picking_form').id, 'form')],
            'target': 'current',
            'res_id': new_picking_id.id,
            'context': dict(self._context),
        }
        


class StockPickingToBatch(models.TransientModel):
    _inherit = "stock.picking.to.batch"

    batch_description = fields.Char(string="Batch Description")

    def attach_pickings(self):
        self.ensure_one()
        pickings = self.env["stock.picking"].browse(self.env.context.get("active_ids"))
        if self.mode == "new":
            company = pickings.company_id
            if len(company) > 1:
                raise UserError(_("The selected pickings should belong to an unique company."))
            batch = self.env["stock.picking.batch"].create(
                {
                    "user_id": self.user_id.id,
                    "company_id": company.id,
                    "picking_type_id": pickings[0].picking_type_id.id,
                    "batch_picking_description": self.batch_description,
                }
            )
        else:
            batch = self.batch_id
            self.batch_id.batch_picking_description = self.batch_description

        pickings.write({"batch_id": batch.id})

    def name_get(self):
        result = []
        for each in self:
            if each.batch_id and each.batch_description:
                name = each.batch_id.name + "/" + each.batch_description
                result.append((each.id, name))
        return result
