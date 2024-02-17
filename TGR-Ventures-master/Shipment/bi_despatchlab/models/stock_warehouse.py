from odoo import models, fields


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"
    _description = "Stock Warehouse"

    is_despatchlab_warehouse = fields.Boolean("Is Despatchlab Warehouse", default=False, copy=False)
