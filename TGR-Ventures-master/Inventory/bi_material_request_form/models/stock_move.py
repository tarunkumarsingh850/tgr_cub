from odoo import _, api, models, fields
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockMove(models.Model):
    _inherit = "stock.move"

    mat_transfer_line_id = fields.Many2one("material.request.line", "Material Transfer Line")

    def _update_reserved_quantity(
        self, need, available_quantity, location_id, lot_id=None, package_id=None, owner_id=None, strict=True
    ):
        """Create or update move lines."""
        self.ensure_one()

        if not lot_id:
            lot_id = self.env["stock.production.lot"]
        if not package_id:
            package_id = self.env["stock.quant.package"]
        if not owner_id:
            owner_id = self.env["res.partner"]

        taken_quantity = min(available_quantity, need)

        # `taken_quantity` is in the quants unit of measure. There's a possibility that the move's
        # unit of measure won't be respected if we blindly reserve this quantity, a common usecase
        # is if the move's unit of measure's rounding does not allow fractional reservation. We chose
        # to convert `taken_quantity` to the move's unit of measure with a down rounding method and
        # then get it back in the quants unit of measure with an half-up rounding_method. This
        # way, we'll never reserve more than allowed. We do not apply this logic if
        # `available_quantity` is brought by a chained move line. In this case, `_prepare_move_line_vals`
        # will take care of changing the UOM to the UOM of the product.
        if not strict and self.product_id.uom_id != self.product_uom:
            taken_quantity_move_uom = self.product_id.uom_id._compute_quantity(
                taken_quantity, self.product_uom, rounding_method="DOWN"
            )
            taken_quantity = self.product_uom._compute_quantity(
                taken_quantity_move_uom, self.product_id.uom_id, rounding_method="HALF-UP"
            )

        quants = []
        rounding = self.env["decimal.precision"].precision_get("Product Unit of Measure")

        if self.product_id.tracking == "serial":
            if float_compare(taken_quantity, int(taken_quantity), precision_digits=rounding) != 0:
                taken_quantity = 0

        try:
            with self.env.cr.savepoint():
                if not float_is_zero(taken_quantity, precision_rounding=self.product_id.uom_id.rounding):
                    # lot passing for material transfer
                    if self.mat_transfer_line_id.lot_ids:
                        quants = (
                            self.env["stock.quant"]
                            .with_context(lot_ids=self.mat_transfer_line_id.lot_ids)
                            ._update_reserved_quantity(
                                self.product_id,
                                location_id,
                                taken_quantity,
                                lot_id=lot_id,
                                package_id=package_id,
                                owner_id=owner_id,
                                strict=strict,
                            )
                        )
                    else:
                        quants = self.env["stock.quant"]._update_reserved_quantity(
                            self.product_id,
                            location_id,
                            taken_quantity,
                            lot_id=lot_id,
                            package_id=package_id,
                            owner_id=owner_id,
                            strict=strict,
                        )
        except UserError:
            taken_quantity = 0

        # Find a candidate move line to update or create a new one.
        for reserved_quant, quantity in quants:
            to_update = next(
                (line for line in self.move_line_ids if line._reservation_is_updatable(quantity, reserved_quant)), False
            )
            if to_update:
                uom_quantity = self.product_id.uom_id._compute_quantity(
                    quantity, to_update.product_uom_id, rounding_method="HALF-UP"
                )
                uom_quantity = float_round(uom_quantity, precision_digits=rounding)
                uom_quantity_back_to_product_uom = to_update.product_uom_id._compute_quantity(
                    uom_quantity, self.product_id.uom_id, rounding_method="HALF-UP"
                )
            if to_update and float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
                to_update.with_context(bypass_reservation_update=True).product_uom_qty += uom_quantity
            else:
                if self.product_id.tracking == "serial":
                    self.env["stock.move.line"].create(
                        [
                            self._prepare_move_line_vals(quantity=1, reserved_quant=reserved_quant)
                            for i in range(int(quantity))
                        ]
                    )
                else:
                    self.env["stock.move.line"].create(
                        self._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)
                    )
        return taken_quantity


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _update_reserved_quantity(
        self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=False
    ):
        """Increase the reserved quantity, i.e. increase `reserved_quantity` for the set of quants
        sharing the combination of `product_id, location_id` if `strict` is set to False or sharing
        the *exact same characteristics* otherwise. Typically, this method is called when reserving
        a move or updating a reserved move line. When reserving a chained move, the strict flag
        should be enabled (to reserve exactly what was brought). When the move is MTS,it could take
        anything from the stock, so we disable the flag. When editing a move line, we naturally
        enable the flag, to reflect the reservation according to the edition.
        :return: a list of tuples (quant, quantity_reserved) showing on which quant the reservation
            was done and how much the system was able to reserve on it
        """
        self = self.sudo()
        rounding = product_id.uom_id.rounding
        quants = self._gather(
            product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict
        )
        reserved_quants = []

        if float_compare(quantity, 0, precision_rounding=rounding) > 0:
            # if we want to reserve
            available_quantity = sum(
                quants.filtered(lambda q: float_compare(q.quantity, 0, precision_rounding=rounding) > 0).mapped(
                    "quantity"
                )
            ) - sum(quants.mapped("reserved_quantity"))
            if float_compare(quantity, available_quantity, precision_rounding=rounding) > 0:
                raise UserError(
                    _(
                        "It is not possible to reserve more products of %s than you have in stock.",
                        product_id.display_name,
                    )
                )
        elif float_compare(quantity, 0, precision_rounding=rounding) < 0:
            # if we want to unreserve
            available_quantity = sum(quants.mapped("reserved_quantity"))
            if float_compare(abs(quantity), available_quantity, precision_rounding=rounding) > 0:
                raise UserError(
                    _(
                        "It is not possible to unreserve more products of %s than you have in stock.",
                        product_id.display_name,
                    )
                )
        else:
            return reserved_quants
        # lot selection for back2back po
        if self._context.get("lot_ids"):
            quants = quants.filtered(lambda x: x.lot_id in self._context.get("lot_ids"))
        # END
        for quant in quants:
            if float_compare(quantity, 0, precision_rounding=rounding) > 0:
                max_quantity_on_quant = quant.quantity - quant.reserved_quantity
                if float_compare(max_quantity_on_quant, 0, precision_rounding=rounding) <= 0:
                    continue
                max_quantity_on_quant = min(max_quantity_on_quant, quantity)
                quant.reserved_quantity += max_quantity_on_quant
                reserved_quants.append((quant, max_quantity_on_quant))
                quantity -= max_quantity_on_quant
                available_quantity -= max_quantity_on_quant
            else:
                max_quantity_on_quant = min(quant.reserved_quantity, abs(quantity))
                quant.reserved_quantity -= max_quantity_on_quant
                reserved_quants.append((quant, -max_quantity_on_quant))
                quantity += max_quantity_on_quant
                available_quantity += max_quantity_on_quant

            if float_is_zero(quantity, precision_rounding=rounding) or float_is_zero(
                available_quantity, precision_rounding=rounding
            ):
                break
        return reserved_quants
