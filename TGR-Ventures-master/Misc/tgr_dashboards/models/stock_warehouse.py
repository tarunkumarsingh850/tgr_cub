from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    dashboard_color = fields.Char("Dashboard Chart RGB Color Code", default="rgb(255, 170, 128)")
