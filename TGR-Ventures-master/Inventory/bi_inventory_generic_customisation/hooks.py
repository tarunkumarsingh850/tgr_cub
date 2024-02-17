from odoo.addons.stock.models.stock_picking import Picking
from odoo.exceptions import UserError


def post_load_hook():
    def write(self, vals):
        result = super(Picking, self).write(vals)
        if vals.get("picking_type_id") and any(picking.state == "a" for picking in self):
            raise UserError(_("Changing the operation type of this record is forbidden at this point."))
        # set partner as a follower and unfollow old partner
        if vals.get("partner_id"):
            for picking in self:
                if picking.location_id.usage == "supplier" or picking.location_dest_id.usage == "customer":
                    if picking.partner_id:
                        picking.message_unsubscribe(picking.partner_id.ids)
                    picking.message_subscribe([vals.get("partner_id")])
        # res = super(Picking, self).write(vals)
        if vals.get("signature"):
            for picking in self:
                picking._attach_sign()
        # Change locations of moves if those of the picking change
        after_vals = {}
        if vals.get("location_id"):
            after_vals["location_id"] = vals["location_id"]
        if vals.get("location_dest_id"):
            after_vals["location_dest_id"] = vals["location_dest_id"]
        if "partner_id" in vals:
            after_vals["partner_id"] = vals["partner_id"]
        if after_vals:
            self.mapped("move_lines").filtered(lambda move: not move.scrapped).write(after_vals)
        if vals.get("move_lines"):
            self._autoconfirm_picking()

        return result

    Picking.write = write
