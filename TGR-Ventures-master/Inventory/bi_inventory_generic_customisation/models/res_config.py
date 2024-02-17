from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    last_days = fields.Integer(
        "Week (Reporting Purpose)", config_parameter="bi_inventory_generic_customisation.last_days"
    )
    product_days = fields.Integer("Product Days", config_parameter="bi_inventory_generic_customisation.product_days")
    product_inventory_account_id = fields.Many2one(
        "account.account",
        string="Product Inventory Account",
        config_parameter="bi_inventory_generic_customisation.product_inventory_account_id",
    )
