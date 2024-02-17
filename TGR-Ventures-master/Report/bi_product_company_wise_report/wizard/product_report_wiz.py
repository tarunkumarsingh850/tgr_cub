from odoo import fields, models


class ProductCompanyWiseReport(models.TransientModel):
    _name = "product.report.wiz"

    product_breeder_id = fields.Many2one(comodel_name="product.breeder", string="Brand")
    categ_id = fields.Many2one(string="Category", comodel_name="product.category")
    company_id = fields.Many2one(comodel_name="res.company", string="Company")

    def get_report_csv(self):
        data = {
            "model": self._name,
            "ids": self.ids,
            "form": {},
        }
        return self.env.ref("bi_product_company_wise_report.product_company_report_excel").report_action(
            self, data=data, config=False
        )

    def get_product_details(self, brand_id, categ_id):
        domain = []
        if brand_id:
            domain.append(("product_breeder_id", "=", brand_id.id))
        if categ_id:
            domain.append(("categ_id", "=", categ_id.id))
        product_templ_id = self.env["product.template"].search(domain)
        product_id = self.env["product.product"].search([("product_tmpl_id", "in", product_templ_id.ids)])
        return product_id
