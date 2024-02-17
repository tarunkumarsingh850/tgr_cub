from odoo import fields, models, api
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    is_company_product_discount = fields.Boolean(
        string="Company Product Discount",
        config_parameter="bi_customer_generic_customization.is_company_product_discount",
    )
    company_res_ids = fields.Many2many("res.company", string="Company")

    dropshipping_product_id = fields.Many2one(
        string="US Shipping Cost Product",
        comodel_name="product.product",
        config_parameter="bi_customer_generic_customization.dropshipping_product_id",
    )
    tgr_percentage = fields.Float(
        string="TGR Percentage",
        config_parameter="bi_customer_generic_customization.tgr_percentage",
    )
    barneys_percentage = fields.Float(
        string="Barneys Percentage",
        config_parameter="bi_customer_generic_customization.barneys_percentage",
    )

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "bi_customer_generic_customization.company_res_ids", self.company_res_ids.ids
        )
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        with_user = self.env["ir.config_parameter"].sudo()
        com_contacts = with_user.get_param("bi_customer_generic_customization.company_res_ids")
        res.update(
            company_res_ids=[(6, 0, literal_eval(com_contacts))] if com_contacts else False,
        )
        return res
