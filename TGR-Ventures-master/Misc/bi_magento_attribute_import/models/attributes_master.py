from odoo import fields, models


class SeedsVariety(models.Model):
    _name = "seeds.variety"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")

class SeedsThcFilter(models.Model):
    _name = "seeds.thc.filter"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")



class SeedsCBDFilter(models.Model):
    _name = "seeds.cbd.filter"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")


class SeedsYieldFilter(models.Model):
    _name = "seeds.yield.filter"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")

class SeedsYieldIndoorFilter(models.Model):
    _name = "seeds.yield.indoor.filter"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")


class SeedsPlantHeight(models.Model):
    _name = "seeds.plant.height"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")


class SeedsFloweringWeeks(models.Model):
    _name = "seeds.flowering.weeks"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")


class SeedsAutoHarvestTime(models.Model):
    _name = "seeds.auto.harvest.time"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")

    
class SeedsClimate(models.Model):
    _name = "seeds.climate"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")

class SeedsOdour(models.Model):
    _name = "seeds.odour"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")


class SeedsGrowDifficulty(models.Model):
    _name = "seeds.grow.difficulty"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")


class SeedsCannabinoidReport(models.Model):
    _name = "seeds.cannabinoid.report"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")


class SeedsGrows(models.Model):
    _name = "seeds.grows"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")

class SeedsBudFormation(models.Model):
    _name = "seeds.bud.formation"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")

class SeedsAwardFilter(models.Model):
    _name = "seeds.award.filter"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")


class SeedsMould(models.Model):
    _name = "seeds.mould"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")

class SeedsExtracts(models.Model):
    _name = "seeds.extracts"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")


class SeedsTasteFilter(models.Model):
    _name = "seeds.taste.filter"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")

class SeedsTerpenes(models.Model):
    _name = "seeds.terpenes"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")

class GeneticDescription(models.Model):
    _name = "genetic.description"

    name = fields.Char('Name')
    magento_attribute_option_id = fields.Char('Magento ID')
    magento_attribute_id = fields.Many2one("magento.product.attribute", string="Magento Attribute", ondelete="cascade")