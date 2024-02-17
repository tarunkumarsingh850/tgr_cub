from odoo import fields, models


class ProductBreeder(models.Model):
    _name = "product.breeder"
    _rec_name = "breeder_name"

    breeder_name = fields.Char(string="Brand Name")
    breeder_des = fields.Char(string="Description")
    discount = fields.Float(string="Discount %")
    tracking = fields.Selection(
        [("serial", "By Unique Serial Number"), ("lot", "By Lots"), ("none", "No Tracking")],
        string="Tracking",
        help="Ensure the traceability of a storable product in your warehouse.",
        default="none",
        required=True,
    )

    magento_id = fields.Char(
        string="Magento ID",
    )
    weight = fields.Float(string="Weight", digits="Stock Weight")
    dimension = fields.Char(string="Dimension")

    def _sync_product_breeder_cron(self, instance):
        m_prod_attr = self.env["magento.attribute.set"]
        instance = self.env["magento.instance"].browse(instance)
        m_prod_attr.import_attribute_set(instance)
