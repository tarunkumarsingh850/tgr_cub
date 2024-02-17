from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    logistics_costs = fields.Float(string="Logistics Costs", compute="_compute_show_cost")

    def _compute_show_cost(self):
        for order in self:
            count = 1
            lines = order.order_line
            logistics_costs = 0
            if order.company_id.is_logistics_company:
                for logistic_line_id in order.company_id.logistics_line_ids:
                    if logistic_line_id.warehouse_id == order.warehouse_id:
                        for line in lines:
                            if line.product_id.detailed_type == "product":
                                if count <= logistic_line_id.per_line:
                                    logistics_costs = logistic_line_id.cost
                                else:
                                    logistics_costs += logistic_line_id.additional_cost
                                count += 1
            order.logistics_costs = logistics_costs
