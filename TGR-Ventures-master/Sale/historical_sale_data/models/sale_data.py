from odoo import fields, models


class HistoricalSaleData(models.Model):
    _name = "historical.sale.data"
    _description = "Historical Sale Data"
    _rec_name = "number"

    number = fields.Char("Sale Order No")
    customer = fields.Char("Customer")
    date = fields.Date("Date")
    state = fields.Selection(
        [
            ("draft", "Quotation"),
            ("sent", "Quotation Sent"),
            ("sale", "Sales Order"),
            ("done", "Locked"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        readonly=True,
        copy=False,
        index=True,
        tracking=3,
        default="draft",
    )
    line_ids = fields.One2many("historical.sale.data.line", "history_id", string="Lines")


class HistoricalSaleDataLine(models.Model):
    _name = "historical.sale.data.line"
    _description = "Historical Sale Data Lines"

    product_id = fields.Many2one("product.template", string="Product")
    quantity = fields.Char("Quantity")
    history_id = fields.Many2one("historical.sale.data", string="history")
    sale_price = fields.Float(
        string="Sale Price",
    )
    product = fields.Char(string="Product")
