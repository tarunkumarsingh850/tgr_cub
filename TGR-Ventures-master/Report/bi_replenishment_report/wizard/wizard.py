from odoo import fields, models


class ReplenishmentWizard(models.TransientModel):
    _name = "replenishment.report"
    _description = "Wizard for replenishment report"

    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", required="1")
    sex_id = fields.Many2one("product.sex", string="Sex")
    inventory_id = fields.Many2one("stock.location", string="Inevntory")
    flower_type_id = fields.Many2one("flower.type", string="Flower Type")
    size_id = fields.Many2one("product.size", string="Size")
    avg_weeks = fields.Integer("Average of Weeks")
    brand_breeder_ids = fields.Many2many("product.breeder", string="Product Brand")
    avg_weeks_for_sale = fields.Integer("Average of weeks for Sale", required="1")
    lead_time_in_weeks = fields.Integer("Lead Time in Weeks")

    def generate_xlsx_report(self):

        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "warehouse_id": self.warehouse_id.id,
                "brand_breeder_id": self.brand_breeder_ids.ids,
                "inventory_id": self.inventory_id.id,
                "flower_type_id": self.flower_type_id.id,
                "sex_id": self.sex_id.id,
                "size_id": self.size_id.id,
                "avg_weeks": self.avg_weeks,
                "avg_weeks_for_sale": self.avg_weeks_for_sale,
                "lead_time_in_weeks": self.lead_time_in_weeks,
            },
        }
        return self.env.ref("bi_replenishment_report.report_replenishment_xlsx").report_action(
            self, data=data, config=False
        )
