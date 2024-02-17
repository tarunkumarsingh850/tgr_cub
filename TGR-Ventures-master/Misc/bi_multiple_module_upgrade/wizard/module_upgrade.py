from odoo import fields, models


class ModuleUpgradeWizard(models.TransientModel):
    _name = "module.upgrade.wizard"
    _description = "Module Upgrade Wizard"

    module_ids = fields.Many2many(
        string="Modules",
        comodel_name="ir.module.module",
    )

    def upgrade_selected_modules(self):
        self.ensure_one()
        self.module_ids.button_immediate_upgrade()
