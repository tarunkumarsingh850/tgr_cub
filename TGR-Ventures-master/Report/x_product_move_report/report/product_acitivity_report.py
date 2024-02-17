from odoo import api, models


class ProductActivityReport(models.AbstractModel):
    _name = "report.x_product_move_report.product_activity_template"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data["form"]["date_from"]
        date_to = data["form"]["date_to"]
        product_id = data["form"]["product_id"]
        location_id = data["form"]["location_id"]
        location = self.env["stock.location"].browse(location_id)
        domain = [("state", "=", "done"), ("product_id", "=", product_id)]
        if date_from:
            domain.append(("date", ">=", date_from))
        if date_to:
            domain.append(("date", "<=", date_to))
        if location_id:
            domain.append("|")
            domain.append(("location_id", "=", location_id))
            domain.append(("location_dest_id", "=", location_id))

        docs = self.env["stock.move.line"].search(domain, order="date ASC")

        count = 0
        move_dict = {}
        product = docs[0].product_id.name
        move_type = {
            "incoming": "IN",
            "outgoing": "OUT",
            "internal": "INT",
        }

        if location_id:
            for each in docs:
                if (
                    each.picking_code == "outgoing"
                    or each.location_dest_id.usage in ["inventory", "transit", "customer"]
                    or (location_id and each.location_id.id == location_id and each.picking_code == "internal")
                ):
                    count = count - each.qty_done
                elif (
                    each.picking_code == "incoming"
                    or (
                        location_id
                        and each.location_dest_id.id == location_id
                        and each.location_dest_id.usage == "internal"
                    )
                    or (each.location_dest_id.usage == "internal" and each.location_id.usage != "internal")
                ):
                    count = count + each.qty_done
                move_dict[each] = int(count)
        else:
            from_location = docs.mapped("location_id.id")
            to_location = docs.mapped("location_dest_id.id")
            stock_location = (
                self.env["stock.location"]
                .search([("usage", "=", "internal")])
                .filtered(lambda location: location.id in from_location or location.id in to_location)
            )
            for location in stock_location:
                count = 0
                line_list = []
                for line in docs.filtered(
                    lambda x: x.location_id.id == location.id or x.location_dest_id.id == location.id
                ):
                    if (
                        line.picking_code == "outgoing"
                        or line.location_dest_id.usage in ["inventory", "transit", "customer"]
                        or (location_id and line.location_id.id == location_id[0] or location.id == line.location_id.id)
                    ):
                        count = count - line.qty_done
                    elif (
                        line.picking_code == "incoming"
                        or (
                            location_id
                            and line.location_dest_id.id == location_id[0]
                            and line.location_dest_id.usage == "internal"
                        )
                        or (line.location_dest_id.usage == "internal" and line.location_id.usage != "internal")
                        or location.id == line.location_dest_id.id
                    ):
                        count = count + line.qty_done
                    line_dict = {line: int(count)}
                    line_list.append(line_dict)
                move_dict[location] = line_list

        return {
            "location_id": location_id,
            "docs": docs,
            "move_type": move_type,
            "data": data,
            "product_name": product,
            "location": location.display_name if location.display_name else "",
            "move_dict": move_dict,
        }
