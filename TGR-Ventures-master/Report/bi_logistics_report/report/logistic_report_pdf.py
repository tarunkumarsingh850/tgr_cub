from odoo import api, models
from datetime import date


class LogisticPDFReport(models.AbstractModel):
    _name = "report.bi_logistics_report.logistic_pdf_report"

    @api.model
    def _get_report_values(self, wizard, data):
        start_date = data["form"]["start_date"]
        end_date = data["form"]["end_date"]
        if data["form"]["logistics_id"]:
            logistics_id = self.env["bi.logistics.master"].search([("id", "=", data["form"]["logistics_id"])])
            logistic_company_id = logistics_id
        warehouse_id = (
            self.env["logistics.master.line"]
            .search([("company_id", "=", self.env.user.company_id.id), ("logistic_id", "=", logistics_id.id)])
            .mapped("warehouse_id")
        )
        sale_order_ids = self.env["sale.order"].search(
            [
                ("date_order", ">=", start_date),
                ("date_order", "<=", end_date),
                ("warehouse_id", "=", warehouse_id.id),
                ("state", "=", "sale"),
            ]
        )

        total_cost = 0
        total_additional_cost = 0
        total_additional_cost_qty = 0
        total_cost_qty = 0
        for order in sale_order_ids:
            no_of_lines = 0
            count = 1
            cost = 0
            cost_qty = 0
            additional_cost_qty = 0
            additional_cost = 0
            cost_per_line = 0
            additional_cost_per_line = 0
            logistics_id = self.env["logistics.master.line"].search(
                [
                    ("company_id", "=", self.env.user.company_id.id),
                    ("logistic_id", "=", logistics_id.id),
                    ("warehouse_id", "=", warehouse_id.id),
                ]
            )
            for line in order.order_line.filtered(lambda l: l.product_id.detailed_type == "product"):
                no_of_lines += 1
                if count <= logistics_id.per_line:
                    cost = logistics_id.cost
                    cost_qty += line.product_uom_qty
                else:
                    additional_cost += logistics_id.additional_cost
                    additional_cost_qty += line.product_uom_qty
                count += 1
            total_cost += cost
            total_additional_cost += additional_cost
            total_cost_qty += cost_qty
            total_additional_cost_qty += additional_cost_qty
            cost_per_line = logistics_id.cost
            additional_cost_per_line = logistics_id.additional_cost
        return {
            "total_cost": total_cost,
            "total_cost_qty": total_cost_qty,
            "cost_per_line": cost_per_line,
            "total_additional_cost": total_additional_cost,
            "total_additional_cost_qty": total_additional_cost_qty,
            "company_id": self.env.user.company_id,
            "additional_cost_per_line": additional_cost_per_line,
            "date": date.today(),
            "logistic_company_id": logistic_company_id,
        }
