from odoo import models


class BatchTransfer(models.AbstractModel):
    _name = "report.bi_batch_transfer_printout.batch_report_template_id"

    def _get_report_values(self, docids, data):
        order_id = self.env["stock.picking.batch"].search([("id", "=", docids[0])])
        length_picking = len(order_id.picking_ids)
        website_id = order_id.picking_ids[0].magento_website_id.id
        website_name = order_id.picking_ids[0].magento_website_id.name
        new_vals = []
        sorted_vals = []
        lines = []
        res_result = []
        if order_id:
            product_zone_ids = self.env["zone.master"].search(
                [
                    ("is_product", "=", True),
                    ("company_id", "=", order_id.company_id.id),
                    ("location_id", "=", order_id.picking_type_id.default_location_src_id.id),
                    ("is_mixed", "=", False),
                ],
                order="number",
            )
            if product_zone_ids:
                for product_zone in product_zone_ids:
                    product_vals = []
                    for line in order_id.move_ids:
                        if line.product_id in product_zone.product_ids:
                            colour = "#000000"
                            green = "#4F7942"
                            blue = "#40B5AD"
                            red = "#FF0000"
                            product_code = ''
                            if line.id not in lines:
                                qty = 0
                                for each_line in order_id.move_ids:
                                    if each_line.product_id == line.product_id:
                                        if each_line != line:
                                            qty += each_line.product_uom_qty
                                            lines.append(each_line.id)
                                if "Auto" in line.product_id.name or "AUTO" in line.product_id.name:
                                    colour = green
                                    product_code = line.product_id.product_tmpl_id.product_breeder_id.breeder_name[:2] + 'A' + line.product_id.name[0]
                                elif "Regular" in line.product_id.name or "REGULAR" in line.product_id.name:
                                    colour = blue
                                    product_code = line.product_id.product_tmpl_id.product_breeder_id.breeder_name[:2] + 'R' + line.product_id.name[0]
                                elif "Feminised" in line.product_id.name or "FEMINISED" in line.product_id.name:
                                    colour = red
                                    product_code = line.product_id.product_tmpl_id.product_breeder_id.breeder_name[:2] + 'F' + line.product_id.name[0]
                                else:
                                    colour = colour


                                product_val = {
                                    "zone": product_zone.name,
                                    "sku": line.product_id.default_code,
                                    "product_id": line.product_id.name,
                                    "pack_size": line.product_id.product_tmpl_id.pack_size_desc,
                                    "quantity": line.product_uom_qty + qty,
                                    "colour": colour,
                                    "flower_type": line.product_id.product_tmpl_id.flower_type_id and line.product_id.product_tmpl_id.flower_type_id.flower_type_des or "",
                                    "brand": line.product_id.product_tmpl_id.product_breeder_id and line.product_id.product_tmpl_id.product_breeder_id.breeder_name or "",
                                    "product_code": product_code,
                                }
                                product_vals.append(product_val)
                                lines.append(line.id)
                        d1 = sorted(product_vals, key=lambda k: k["brand"])
                        # d1 = sorted(product_vals, key=lambda k: k["product_id"])
                        d = sorted(d1, key=lambda x: x['product_code'] and (x['product_code'][0], x['product_code'][1],x['product_code'][2],x['product_code'][3]) or ())
                sorted_vals += d
            zone_ids = self.env["zone.master"].search(
                [
                    ("company_id", "=", order_id.company_id.id),
                    ("location_id", "=", order_id.picking_type_id.default_location_src_id.id),
                    ("is_mixed", "=", False),
                ],
                order="number",
            )
            for zone in zone_ids:
                vals = []
                for line in order_id.move_ids:
                    if zone.brand_ids and not zone.is_product:
                        if line.product_id.product_tmpl_id.product_breeder_id in zone.brand_ids:
                            qty = 0
                            for each_line in order_id.move_ids:
                                if each_line.product_id == line.product_id:
                                    if each_line != line:
                                        qty += each_line.product_uom_qty
                                        lines.append(each_line.id)

                            colour = "#000000"
                            green = "#4F7942"
                            blue = "#40B5AD"
                            red = "#FF0000"
                            product_code = ""
                            if line.id not in lines:
                                lines.append(line.id)
                                if "Auto" in line.product_id.name or "AUTO" in line.product_id.name:
                                    colour = green
                                    product_code = line.product_id.product_tmpl_id.product_breeder_id.breeder_name[:2] + 'A' + line.product_id.name[0]
                                elif "Regular" in line.product_id.name or "REGULAR" in line.product_id.name:
                                    colour = blue
                                    product_code = line.product_id.product_tmpl_id.product_breeder_id.breeder_name[:2] + 'R' + line.product_id.name[0]
                                elif "Feminised" in line.product_id.name or "FEMINISED" in line.product_id.name:
                                    colour = red
                                    product_code = line.product_id.product_tmpl_id.product_breeder_id.breeder_name[:2] + 'F' + line.product_id.name[0]
                                else:
                                    colour = colour
                                val = {
                                    "zone": zone.name,
                                    "sku": line.product_id.default_code,
                                    "product_id": line.product_id.name,
                                    "pack_size": line.product_id.product_tmpl_id.pack_size_desc,
                                    "quantity": line.product_uom_qty + qty,
                                    "colour": colour,
                                    "flower_type": line.product_id.product_tmpl_id.flower_type_id and line.product_id.product_tmpl_id.flower_type_id.flower_type_des or "",
                                    "brand": line.product_id.product_tmpl_id.product_breeder_id and line.product_id.product_tmpl_id.product_breeder_id.breeder_name or "",
                                    "product_code": product_code,
                                }
                                vals.append(val)
                    d1 = sorted(vals, key=lambda k: k["brand"])
                    # d = sorted(vals, key=lambda k: k["product_id"])
                    # d2 = sorted(d1, key=lambda k: k["flower_type"])
                    d = sorted(d1, key=lambda x: x['product_code'] and (x['product_code'][0], x['product_code'][1],x['product_code'][2],x['product_code'][3]) or ())
                res_result += d
            product_code = ''
            for line in order_id.move_ids:
                colour = "#000000"
                green = "#4F7942"
                blue = "#40B5AD"
                red = "#FF0000"
                if line.id not in lines:
                    qty = 0
                    for each_line in order_id.move_ids:
                        if each_line.product_id == line.product_id:
                            if each_line != line:
                                qty += each_line.product_uom_qty
                                lines.append(each_line.id)
                    if "Auto" in line.product_id.name or "AUTO" in line.product_id.name:
                        colour = green
                        product_code = line.product_id.product_tmpl_id.product_breeder_id.breeder_name[:2] + 'A' + line.product_id.name[0]
                    elif "Regular" in line.product_id.name or "REGULAR" in line.product_id.name:
                        colour = blue
                        product_code = line.product_id.product_tmpl_id.product_breeder_id.breeder_name[:2] + 'R' + line.product_id.name[0]
                    elif "Feminised" in line.product_id.name or "FEMINISED" in line.product_id.name:
                        colour = red
                        product_code = line.product_id.product_tmpl_id.product_breeder_id.breeder_name[:2] + 'F' + line.product_id.name[0]
                    else:
                        colour = colour
                    new_val = {
                        "sku": line.product_id.default_code,
                        "product_id": line.product_id.name,
                        "pack_size": line.product_id.product_tmpl_id.pack_size_desc,
                        "quantity": line.product_uom_qty + qty,
                        "colour": colour,
                        "flower_type": line.product_id.product_tmpl_id.flower_type_id and line.product_id.product_tmpl_id.flower_type_id.flower_type_des or "",
                        "brand": line.product_id.product_tmpl_id.product_breeder_id and line.product_id.product_tmpl_id.product_breeder_id.breeder_name or "",
                        "product_code":product_code
                    }
                    new_vals.append(new_val)
            new_vals1 = sorted(new_vals, key=lambda k: k["brand"])
            new_vals = sorted(new_vals1, key=lambda x: x['product_code'] and (x['product_code'][0], x['product_code'][1],x['product_code'][2],x['product_code'][3]) or ())
        return {
            "docs": order_id,
            "zone_vals": res_result,
            "product_vals": sorted_vals,
            "new_vals": new_vals,
            "website_id": website_id,
            "website_name": website_name,
            "length_picking": length_picking,
        }
