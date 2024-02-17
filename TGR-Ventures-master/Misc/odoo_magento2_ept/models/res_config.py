from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    delivery_last_day = fields.Integer("Delivery Last Day", config_parameter="odoo_magento2_ept.delivery_last_day")
