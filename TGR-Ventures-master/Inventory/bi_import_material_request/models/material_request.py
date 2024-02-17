from odoo import _, models


class MaterialRequest(models.Model):
    _inherit = "material.request"

    def action_import(self):
        return {
            "name": _("Import Lines"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "material.request.wizard",
            "context": {"default_material_update_id": self.id},
            "target": "new",
        }
