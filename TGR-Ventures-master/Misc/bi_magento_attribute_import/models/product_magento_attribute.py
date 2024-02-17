from odoo import fields, models, api


class ProductMagentoAttribte(models.Model):
    _name = "product.magento.attribute"
    _description = "Model is used to store the product magento attribute"

    magento_attribute_id = fields.Many2one(
        string="Magento Attribute",
        comodel_name="magento.attribute",
    )
    name = fields.Char(
        string="Name",
    )
    attribute_id = fields.Many2one(
        string="Attribute",
        comodel_name="magento.product.attribute",
    )
    attribute_val_id = fields.Many2one(
        string="Attribute Val",
        comodel_name="magento.attribute.option",
    )

    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.template",
    )

    @api.onchange("attribute_id")
    def _onchange_attribute_id(self):
        attribute_vals = []
        if self.attribute_id:
            attribute_val_ids = self.env["magento.attribute.option"].search(
                [("magento_attribute_id", "=", self.attribute_id.id)]
            )
            for each in attribute_val_ids:
                attribute_vals.append(each.id)
            domain = {"attribute_val_id": [("id", "in", attribute_vals)]}
            result = {"domain": domain}
            return result
