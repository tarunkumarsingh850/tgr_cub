from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    folder_for_barneys_so_data = fields.Char(
        "Folder for Barneys data files",
        config_parameter="bi_barneys_ecommerce_api.barneys_files_folder_path",
        help="Folder that contain the  files",
    )
    shipping_cost_product_id = fields.Many2one(
        "product.template",
        string="Shipping Cost Product",
        related="company_id.shipping_cost_product_id",
        readonly=False,
    )
    picking_packing_cost = fields.Monetary(
        "Picking/Packing Cost", related="company_id.picking_packing_cost", readonly=False
    )
    min_pick_pack_cost_upto_sku_count = fields.Integer(
        "Minimum Picking/Packing Cost upto SKU Count",
        related="company_id.min_pick_pack_cost_upto_sku_count",
        readonly=False,
    )
    additional_picking_packing_cost = fields.Monetary(
        "Additional Picking/Packing Cost", related="company_id.additional_picking_packing_cost", readonly=False
    )
    barneys_payment_surcharge = fields.Monetary(
        "Payment Surcharge", related="company_id.barneys_payment_surcharge", readonly=False
    )
    tgr_percentage = fields.Float("TGR Percentage", related="company_id.tgr_percentage", readonly=False)
    barneys_percentage = fields.Float("Barneys Percentage", related="company_id.barneys_percentage", readonly=False)

    def download_barneys_sample_xml(self):
        """
        Download sample xml file for put inside the folder
        """
        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": "/bi_barneys_ecommerce_api/static/sample/xml/sample_xml.zip",
        }

    def download_barneys_sample_csv(self):
        """
        Download sample csv file for put inside the folder
        """
        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": "/bi_barneys_ecommerce_api/static/sample/csv/sample_csv.zip",
        }
