from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    magento_attribute_ids = fields.One2many(
        string="Magento Attribute",
        comodel_name="product.magento.attribute",
        inverse_name="product_id",
    )
    seeds_variety_id = fields.Many2one('seeds.variety', '​Variety')
    seeds_thc_filter_id = fields.Many2one('seeds.thc.filter', 'THCV Content %')
    seeds_cbd_filter_id = fields.Many2one('seeds.cbd.filter', 'CBD Content %')
    seeds_yield_filter_id = fields.Many2one('seeds.yield.filter', 'Yield Outdoor gr/plant')
    seeds_yield_indoor_filter_id = fields.Many2one('seeds.yield.indoor.filter', 'Yield indoor gr/m2')
    seeds_plant_height_id = fields.Many2one('seeds.plant.height', 'Plant Height cm')
    seeds_flowering_weeks_id = fields.Many2one('seeds.flowering.weeks', 'Flowering Time')
    seeds_auto_harvest_time_id = fields.Many2one('seeds.auto.harvest.time', 'Seeds To Harvest Time')
    seeds_variety_id = fields.Many2one('seeds.variety', 'Seeds Variety')
    seeds_thc_filter_id = fields.Many2one('seeds.thc.filter', 'Seeds THC Filter')
    seeds_cbd_filter_id = fields.Many2one('seeds.cbd.filter', 'Seeds CBD Filter')
    seeds_yield_filter_id = fields.Many2one('seeds.yield.filter', 'Seeds Yeild Filter')
    seeds_yield_indoor_filter_id = fields.Many2one('seeds.yield.indoor.filter', 'Seeds Yeild Indoor Filter')
    seeds_plant_height_id = fields.Many2one('seeds.plant.height', 'Seeds Plant Height')
    seeds_flowering_weeks_id = fields.Many2one('seeds.flowering.weeks', 'Seeds Flowering Weeks')
    seeds_auto_harvest_time_id = fields.Many2one('seeds.auto.harvest.time', 'Seeds Auto Harvest Time')
    seeds_climate_id = fields.Many2one('seeds.climate', 'Seeds Climate')
    seeds_odour_id = fields.Many2one('seeds.odour', 'Seeds Odour')
    seeds_grow_difficulty_id = fields.Many2one('seeds.grow.difficulty', 'Seeds Grow difficulty')
    seeds_cannabinoid_report_id = fields.Many2one('seeds.cannabinoid.report', 'Seeds Cannabinoid Report')
    seeds_grows_id = fields.Many2one('seeds.grows', 'Seeds Grows')
    seeds_bud_formation_id = fields.Many2one('seeds.bud.formation', 'Seeds Bud Formation')
    seeds_award_filter_id = fields.Many2one('seeds.award.filter', 'Seeds Award Filter')
    seeds_mould_id = fields.Many2one('seeds.mould', 'Seeds Mould')
    seeds_extracts_id = fields.Many2one('seeds.extracts', 'Seeds Extract')
    seeds_taste_filter_id = fields.Many2one('seeds.taste.filter', 'Seeds Taste Filter')
    seeds_terpenes_id = fields.Many2one('seeds.terpenes', 'Seeds Terpenes')
    genetic_discription_id = fields.Many2one('genetic.description', 'Genetic Description')
