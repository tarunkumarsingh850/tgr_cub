from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # override the action confirm for overcome location security
    def action_confirm(self):
        self._check_company()
        self.mapped("package_level_ids").filtered(lambda pl: pl.state == "draft" and not pl.move_ids)._generate_moves()
        # call `_action_confirm` on every draft move
        self.mapped("move_lines").sudo().filtered(lambda move: move.state == "draft").sudo()._action_confirm()

        # run scheduler for moves forecasted to not have enough in stock
        self.mapped("move_lines").filtered(
            lambda move: move.state not in ("draft", "cancel", "done")
        )._trigger_scheduler()
        return True

    def _action_done(self):
        """Call `_action_done` on the `stock.move` of the `stock.picking` in `self`.
        This method makes sure every `stock.move.line` is linked to a `stock.move` by either
        linking them to an existing one or a newly created one.

        If the context key `cancel_backorder` is present, backorders won't be created.

        :return: True
        :rtype: bool
        """
        self._check_company()

        todo_moves = self.mapped("move_lines").filtered(
            lambda self: self.state in ["draft", "waiting", "partially_available", "assigned", "confirmed"]
        )
        for picking in self:
            if picking.owner_id:
                picking.move_lines.write({"restrict_partner_id": picking.owner_id.id})
                picking.move_line_ids.write({"owner_id": picking.owner_id.id})
        todo_moves.sudo()._action_done(cancel_backorder=self.env.context.get("cancel_backorder"))
        self.write({"date_done": fields.Datetime.now(), "priority": "0"})

        # if incoming moves make other confirmed/partially_available moves available, assign them
        done_incoming_moves = self.filtered(lambda p: p.picking_type_id.code == "incoming").move_lines.filtered(
            lambda m: m.state == "done"
        )
        done_incoming_moves._trigger_assign()

        self._send_confirmation_email()
        return True
