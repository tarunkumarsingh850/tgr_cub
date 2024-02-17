from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    is_logistics_company = fields.Boolean(
        string="Is Logistics Company",
    )
    logistics_line_ids = fields.One2many(
        string="Logistics",
        comodel_name="logistics.master.line",
        inverse_name="company_id",
    )


class LogisticsMasterLine(models.Model):
    _name = "logistics.master.line"
    _description = "Model to store the logistics cost"

    logistic_id = fields.Many2one(
        string="Logistic",
        comodel_name="bi.logistics.master",
    )
    cost = fields.Float(string="Cost")
    additional_cost = fields.Float(string="Additional Cost Per Line")
    monthly_fee = fields.Float(string="Monthly Fee")
    per_line = fields.Integer(
        string="Up to Line",
    )
    warehouse_id = fields.Many2one("stock.warehouse")

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
    )
