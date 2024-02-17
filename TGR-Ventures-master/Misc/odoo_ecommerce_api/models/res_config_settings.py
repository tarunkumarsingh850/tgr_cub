from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    folder_for_so_data = fields.Char(
        "Folder for data files",
        config_parameter="odoo_ecommerce_api.files_folder_path",
        help="Folder that contain the  files",
    )
    dropshipping_shipping_cost = fields.Float(
        string="Shipping Cost", related="company_id.dropshipping_shipping_cost", readonly=False
    )
    dropshipping_picking_packing_cost = fields.Monetary(
        "Picking/Packing Cost", related="company_id.dropshipping_picking_packing_cost", readonly=False
    )
    dropshipping_min_pick_pack_cost_upto_sku_count = fields.Integer(
        "Minimum Picking/Packing Cost upto SKU Count",
        related="company_id.dropshipping_min_pick_pack_cost_upto_sku_count",
        readonly=False,
    )
    dropshipping_additional_picking_packing_cost = fields.Monetary(
        "Additional Picking/Packing Cost",
        related="company_id.dropshipping_additional_picking_packing_cost",
        readonly=False,
    )
    dropshipping_payment_surcharge = fields.Monetary(
        "Payment Surcharge", related="company_id.dropshipping_payment_surcharge", readonly=False
    )

    def download_sample_xml(self):
        """
        Download sample xml file for put inside the folder
        """
        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": "/odoo_ecommerce_api/static/sample/xml/sample_xml.zip",
        }

    def download_sample_csv(self):
        """
        Download sample csv file for put inside the folder
        """
        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": "/odoo_ecommerce_api/static/sample/csv/sample_csv.zip",
        }
