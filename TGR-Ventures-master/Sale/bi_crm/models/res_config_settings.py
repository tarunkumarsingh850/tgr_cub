from odoo import fields, models, api
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    res_user_id = fields.Many2one("res.users", string="Email From")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param("bi_crm.res_user_id", self.res_user_id.id)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        with_user = self.env["ir.config_parameter"].sudo()
        res_users = with_user.get_param("bi_crm.res_user_id")
        res.update(
            res_user_id=literal_eval(res_users) if res_users else False,
        )
        return res
