from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.tools.misc import get_lang
import datetime


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    eta_date = fields.Date("ETA")
    is_created_picking = fields.Boolean("is_created_picking", default=False, copy=False)

    acumatica_po_status = fields.Selection(
        string="Acumatica PO Status",
        selection=[
            ("on_hand", "On Hand"),
            ("On Hold", "On Hold"),
            ("pending_approval", "Pending Approval"),
            ("rejected", "Rejected"),
            ("open", "Open"),
            ("pending_printing", "Pending Printing"),
            ("pending_email", "Pending Email"),
            ("canceled", "Canceled"),
            ("completed", "Completed"),
            ("closed", "Closed"),
            ("printed", "Printed"),
            ("is_empty", "Is Empty"),
        ],
    )
    billing_status = fields.Selection(
        [
            ("no", "Nothing to Bill"),
            ("to invoice", "Waiting Bills"),
            ("invoiced", "Fully Billed"),
        ],
        string="Billing Status",
        store=True,
        readonly=True,
        copy=False,
        default="no",
    )

    trigger_boolean = fields.Boolean(
        string="trigger_boolean",
        compute="_compute_trigger_boolean",
    )
    lead_days = fields.Integer(string="Lead Days")
    is_balance_picking = fields.Boolean(string="Is Balance Picking", compute="_compute_is_balance_picking", copy=False)
    is_eta_color = fields.Boolean(string="Is ETA Color", default=False, compute="_compute_eta_color")
    arrival_status = fields.Selection(
        [("nil", "Nil"), ("not_arrived", "Not Arrived"), ("arrived", "Arrived"), ("sent", "Sent")], default="nil"
    )
    arrival_date = fields.Date("Arrival Date")
    mark_as_fully_billed = fields.Boolean(string="Mark as Fully Billed", default=False)

    def _compute_eta_color(self):
        for record in self:
            is_eta_color = False
            if record.billing_status == "no":
                if record.eta_date:
                    if record.eta_date < date.today():
                        is_eta_color = True
            record.is_eta_color = is_eta_color

    def unlink_lines(self):
        for record in self:
            if record.order_line:
                record.order_line.unlink()

    @api.depends("order_line")
    def _compute_is_balance_picking(self):
        is_balance_picking = False
        for record in self:
            for line in record.order_line:
                if line.product_id.detailed_type == "product":
                    if line.product_qty > line.qty_received:
                        is_balance_picking = True
                        break
            record.is_balance_picking = is_balance_picking

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        self.lead_days = self.partner_id.lead_days

    def _compute_trigger_boolean(self):
        self.trigger_boolean = False
        for record in self:
            if record.mark_as_fully_billed:
                billing_status = "invoiced"
            else:
                billing_status = "no"
                if record.incoming_picking_count == 0 and record.state == "purchase":
                    billing_status = "no"
                check_picking = False
                if record.incoming_picking_count > 0:
                    picking_state = record.picking_ids.mapped("state")
                    if "done" not in picking_state:
                        check_picking = True
                    elif "done" in picking_state:
                        check_picking = False
                    if check_picking == False:
                        billing_status = "to invoice"
                    else:
                        billing_status = "no"
                check_invoice = False
                if record.invoice_count > 0:
                    # for bill_state in record.invoice_ids.mapped('state'):
                    #     if bill_state not in ['posted','cancel']:
                    #         check_invoice = True
                    #     if bill_state in ['cancel']:
                    #         check_invoice = True
                    bill_state = record.invoice_ids.mapped("state")
                    if "posted" not in bill_state:
                        check_invoice = True
                    elif "posted" in bill_state:
                        check_invoice = False
                    if not check_invoice:
                        billing_status = "invoiced"
                # if record.name in [
                #     "P00111",
                #     "P00112",
                #     "P00113",
                #     "P00116",
                #     "P00117",
                #     "2022009310",
                #     "2022009262",
                #     "2022008860",
                # ]:
                #     billing_status = "to invoice"
                if record.name in ["2022009354", "2022009350", "2022009304"]:
                    billing_status = "invoiced"
            record.billing_status = billing_status

    def button_create_picking(self, force=False):
        self._create_picking()
        self.is_created_picking = True
        picking_vals = self.picking_ids.filtered(lambda x: x.origin == self.name)
        if picking_vals:
            picking_vals.note = self.notes
            receipt = self.env["reason.code"].search([("name", "=", "Direct Receipt")], limit=1)
            if receipt:
                picking_vals.reason_code_id = receipt.id
            else:
                reason = self.env["ir.config_parameter"].sudo().get_param("bi_reason_code.purchase_reason_id")
                if reason:
                    picking_vals.reason_code_id = int(reason)
                else:
                    picking_vals.reason_code_id = False

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for line in self.order_line:
            if line.product_qty < line.product_id.case_quantity:
                raise UserError(_(f"Quantity of {line.product_id.name} should be greater than Case Quantity"))
        return res

    @api.onchange("date_order", "partner_id")
    def _onchange_eta_date(self):
        if self.date_order:
            self.eta_date = self.date_order + timedelta(days=self.partner_id.lead_days)
        else:
            self.eta_date = False

    @api.model
    def _get_picking_type(self, company_id):
        if company_id == 10:
            picking_type = self.env["stock.picking.type"].search([("id", "=", 97)])
            if picking_type:
                return picking_type
        else:
            picking_type = self.env["stock.picking.type"].search(
                [("code", "=", "incoming"), ("warehouse_id.company_id", "=", company_id)]
            )
            if not picking_type:
                picking_type = self.env["stock.picking.type"].search(
                    [("code", "=", "incoming"), ("warehouse_id", "=", False)]
                )
        return picking_type[:1]

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        if self.picking_ids:
            bill_date = max(self.picking_ids.filtered(lambda pick: pick.state == "done").mapped("date_done"))
            if bill_date:
                res.update(
                    {
                        "invoice_date": bill_date,
                        "date": bill_date,
                        "l10n_es_registration_date": bill_date,
                        "narration": self.notes,
                        "receipt_date": bill_date,
                    }
                )
        return res

    @api.onchange("arrival_status")
    def _onchange_arrival_status(self):
        for rec in self:
            if rec.arrival_status == "arrived":
                rec.arrival_date = datetime.datetime.now()
            else:
                rec.arrival_date = ""

    @api.onchange("picking_type_id")
    def onchange_picking_type_id(self):
        for rec in self:
            if rec.picking_type_id.warehouse_id:
                for line in rec.order_line:
                    line.warehouse_dest_id = rec.picking_type_id.warehouse_id.id


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    price_unit = fields.Float(string="Unit Price", required=True, digits=(12, 3))
    product_sku = fields.Char('SKU', related='product_id.default_code')
    last_purchase_cost = fields.Float(string='Last Purchase Cost')
    is_not_update_cost = fields.Boolean('Is Not Update Cost')

    ##Overriding function for loading vendor tax against product
    def _product_id_change(self):
        if not self.product_id:
            return

        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        product_lang = self.product_id.with_context(
            lang=get_lang(self.env, self.partner_id.lang).code,
            partner_id=self.partner_id.id,
            company_id=self.company_id.id,
        )
        self.name = self._get_product_purchase_description(product_lang)
        if self.order_id.partner_id.taxes_ids:
            self.write({"taxes_id": [(6, 0, self.order_id.partner_id.taxes_ids.ids)]})
        else:
            self._compute_tax_id()

    @api.onchange("product_id")
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if self.product_id:
            product_warehouse_id = self.product_id.default_warehouse_id
            picking_type_id = self.order_id.picking_type_id
            self.name = self.product_id.name
            if self.product_id and self.product_id.seller_ids:
                seller_ids = self.product_id.seller_ids.filtered(
                    lambda l: l.name == self.order_id.partner_id and l.price > 0
                )
                if seller_ids:
                    self.last_purchase_cost = seller_ids[0].price
            if (
                product_warehouse_id
                and picking_type_id
                and picking_type_id.warehouse_id
                and product_warehouse_id != picking_type_id.warehouse_id
            ):
                self.warehouse_dest_id = picking_type_id.warehouse_id.id
            elif not product_warehouse_id and picking_type_id and picking_type_id.warehouse_id:
                self.warehouse_dest_id = picking_type_id.warehouse_id.id
        return res
    

    def unlink(self):
        for line in self:
            move_id = self.env['stock.move'].search([('purchase_line_id','=',line.id)])
            if line.qty_received == 0.00 and line.order_id.state == 'purchase' and move_id.picking_id.state == 'done':
                if move_id.product_id.id == line.product_id.id:
                    move_id.state = 'draft'
                    move_id.unlink()
            res = super(PurchaseOrderLine,self).unlink()
            return res
    

    @api.ondelete(at_uninstall=False)
    def _unlink_except_purchase_or_done(self):
        for line in self:
            if line.order_id.state in ['purchase', 'done']:
                state_description = {state_desc[0]: state_desc[1] for state_desc in self._fields['state']._description_selection(self.env)}
                # raise UserError(_('Cannot delete a purchase order line which is in state \'%s\'.') % (state_description.get(line.state),))
    