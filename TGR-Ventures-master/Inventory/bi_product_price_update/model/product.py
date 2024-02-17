from odoo import fields, models, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'


    def _product_price_updation(self):
        if self.env.company.id == 9: 
            for rec in self.search([('eu_tiger_one_boolean','=',True),('eu_seedsman_boolean','=',True),('detailed_type','=','product')]):
                value = rec.product_variant_id.with_company(10).last_cost_2
                rec.sudo().write({
                    'last_cost_2':value
                })