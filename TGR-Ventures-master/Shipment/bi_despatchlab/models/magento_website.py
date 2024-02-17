from odoo import models, fields


class MagentoWebsite(models.Model):
    _inherit = "magento.website"
    _description = "Magento Website"

    delivery_country_line_ids = fields.One2many("website.delivery.country.line", "website_id", string="Delivery Line")
    tax_country_line_ids = fields.One2many('website.tax.country.line', 'website_id', string='Country base Tax Line')


class MagentoWebsiteDeliveryCountryLine(models.Model):
    _name = "website.delivery.country.line"
    _description = "Magento Website Delivery Country Line"

    website_id = fields.Many2one("magento.website", string="Website")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    country_ids = fields.Many2many("res.country", string="Country")




class MagentoWebsiteTaxCountryLine(models.Model):
    _name = "website.tax.country.line"
    _description = "Magento Website tax Country Line"

    website_id = fields.Many2one("magento.website", string="Website")
    country_id = fields.Many2one("res.country", string="Country")
    tax_id = fields.Many2one('account.tax', String="Tax")
