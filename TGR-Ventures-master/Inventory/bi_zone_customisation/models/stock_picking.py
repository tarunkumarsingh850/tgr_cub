from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    zone_id = fields.Many2one(string="Zone", comodel_name="zone.master", compute="_compute_zone_id", store=True)
    is_mixed_zone = fields.Boolean(
        string="is_mixed_zone",
    )

    @api.depends("move_ids_without_package")
    def _compute_zone_id(self):
        for record in self:
            # zone = False
            product_brand_ids = []
            if record.move_ids_without_package:
                free_products_lst = record.move_ids_without_package.mapped("product_id").product_tmpl_id.mapped(
                    "is_free_product"
                )
                all_free_products = False
                if all(free_products_lst):
                    all_free_products = True
                if not all_free_products:
                    for line in record.move_ids_without_package:
                        if (
                            not line.product_id.product_tmpl_id.is_free_product
                            and line.product_id.product_tmpl_id.product_breeder_id.id not in product_brand_ids
                        ):
                            product_brand_ids.append(line.product_id.product_tmpl_id.product_breeder_id.id)
                    zone_id = self.env["zone.master"].search(
                        [
                            ("company_id", "=", record.company_id.id),
                            ("location_id", "=", record.location_id.id),
                            ("brand_ids", "in", product_brand_ids),
                        ]
                    )
                else:
                    for line in record.move_ids_without_package:
                        if line.product_id.product_tmpl_id.product_breeder_id.id not in product_brand_ids:
                            product_brand_ids.append(line.product_id.product_tmpl_id.product_breeder_id.id)
                    zone_id = self.env["zone.master"].search(
                        [
                            ("company_id", "=", record.company_id.id),
                            ("location_id", "=", record.location_id.id),
                            ("brand_ids", "in", product_brand_ids),
                        ]
                    )
                if zone_id:
                    if len(zone_id) == 1:
                        zone = zone_id
                    else:
                        zone = self.env["zone.master"].search(
                            [("company_id", "=", record.company_id.id), ("is_mixed", "=", True)], limit=1
                        )
                        record.is_mixed_zone = True
                    record.zone_id = zone.id
                else:
                    record.zone_id = False
