from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    despatchlab_warehouse_id = fields.Many2one(
        "stock.warehouse", string="Despatchlab Warehouse", related="company_id.despatchlab_warehouse_id", readonly=False
    )
    despatchlab_partner_ids = fields.Many2many(
        "res.partner", string="Despatchlab Partners", related="company_id.despatchlab_partner_ids", readonly=False
    )
    despatchlab_username = fields.Char("Username", related="company_id.despatchlab_username", readonly=False)
    despatchlab_password = fields.Char("Password", related="company_id.despatchlab_password", readonly=False)
