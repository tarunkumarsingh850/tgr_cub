from odoo import fields, models, _


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    count_paid_orders = fields.Integer(compute="_compute_orders")
    count_unpaid_orders = fields.Integer(compute="_compute_orders")
    count_credit_customer = fields.Integer(compute="_compute_orders")
    count_is_hold = fields.Integer(compute="_compute_orders")
    count_high_alert_customer = fields.Integer(compute="_compute_orders")
    count_usa_charge_back = fields.Integer(compute="_compute_orders")

    def _compute_orders(self):
        domains = {
            "count_is_hold": [("is_hold", "=", True)],
            "count_paid_orders": [("payment_status", "=", "paid")],
            "count_unpaid_orders": [("payment_status", "=", "not_paid")],
            "count_credit_customer": [("is_credit_customer", "=", True)],
            "count_high_alert_customer": [("partner_id.high_alert_customer", "=", True)],
            "count_usa_charge_back": [("partner_id.usa_charge_back", "=", True)],
        }
        for field in domains:
            data = self.env["stock.picking"].read_group(
                domains[field] + [("state", "not in", ("done", "cancel")), ("picking_type_id", "in", self.ids)],
                ["picking_type_id"],
                ["picking_type_id"],
            )
            count = {x["picking_type_id"][0]: x["picking_type_id_count"] for x in data if x["picking_type_id"]}
            for record in self:
                record[field] = count.get(record.id, 0)

    def get_action_picking_paid_orders_tree(self):
        picking_ids = self.env["stock.picking"].search(
            [
                ("state", "not in", ("done", "cancel")),
                ("payment_status", "=", "paid"),
                ("picking_type_id", "in", self.ids),
            ]
        )
        return {
            "name": _("Paid Orders"),
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": [("id", "in", picking_ids.ids)],
        }

    def get_action_picking_hold_orders_tree(self):
        picking_ids = self.env["stock.picking"].search(
            [("state", "not in", ("done", "cancel")), ("is_hold", "=", True), ("picking_type_id", "in", self.ids)]
        )
        return {
            "name": _("Hold Orders"),
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": [("id", "in", picking_ids.ids)],
        }

    def get_action_picking_unpaid_orders_tree(self):
        picking_ids = self.env["stock.picking"].search(
            [
                ("state", "not in", ("done", "cancel")),
                ("payment_status", "=", "not_paid"),
                ("picking_type_id", "in", self.ids),
            ]
        )
        return {
            "name": _("Unpaid Orders"),
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": [("id", "in", picking_ids.ids)],
        }

    def get_action_picking_credit_customers_orders_tree(self):
        picking_ids = self.env["stock.picking"].search(
            [
                ("state", "not in", ("done", "cancel")),
                ("is_credit_customer", "=", True),
                ("picking_type_id", "in", self.ids),
            ]
        )
        return {
            "name": _("Credit Customer Orders"),
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": [("id", "in", picking_ids.ids)],
        }

    def get_action_picking_high_alert_customer(self):
        picking_ids = self.env["stock.picking"].search(
            [
                ("state", "not in", ("done", "cancel")),
                ("partner_id.high_alert_customer", "=", True),
                ("picking_type_id", "in", self.ids),
            ]
        )
        return {
            "name": _("High Alert Orders"),
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": [("id", "in", picking_ids.ids)],
        }

    def get_action_picking_usa_charge_back(self):
        picking_ids = self.env["stock.picking"].search(
            [
                ("state", "not in", ("done", "cancel")),
                ("partner_id.usa_charge_back", "=", True),
                ("picking_type_id", "in", self.ids),
            ]
        )
        return {
            "name": _("USA Charge Back"),
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": [("id", "in", picking_ids.ids)],
        }
