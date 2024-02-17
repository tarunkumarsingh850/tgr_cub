from odoo import fields, models, tools

TRANSACTION_TYPES = [
    ("current", "CURRENT"),
    ("internal", "INTERNAL"),
    ("purchase", "PURCHASE"),
    ("sale", "SALES"),
]


class StockForecastAnalysis(models.Model):
    _name = "stock.forecast.analysis"
    _description = "Inventory Forecast Analysis"
    _auto = False

    date = fields.Date(string="Date")
    product_id = fields.Many2one("product.product", string="Product", readonly=True)
    product_tmpl_id = fields.Many2one(
        "product.template", string="Product Template", related="product_id.product_tmpl_id", readonly=True
    )
    cumulative_quantity = fields.Float(string="Cumulative Quantity (Day)", readonly=True)
    cumulative_quantity_week = fields.Float(string="Cumulative Quantity (Week)", readonly=True)
    cumulative_quantity_month = fields.Float(string="Cumulative Quantity (Month)", readonly=True)
    quantity = fields.Float(readonly=True)
    company_id = fields.Many2one("res.company", string="Company", readonly=True)
    product_category_id = fields.Many2one("product.category", string="Product Category", readonly=True)
    partner_id = fields.Many2one("res.partner", string="Picking Partner", readonly=True)
    location_id = fields.Many2one("stock.location", string="Location", readonly=True)
    transaction_type = fields.Selection(TRANSACTION_TYPES, string="Transaction Type", readonly=True)
    reference = fields.Char(string="Reference", readonly=True)
    product_code = fields.Char(string="Internal Reference", readonly=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "stock_forecast_analysis")
        self.env.cr.execute(
            """CREATE OR REPLACE VIEW stock_forecast_analysis AS (
                WITH
                    company_date AS (
                        SELECT
                            rc.id,
                            (CURRENT_TIMESTAMP AT TIME ZONE COALESCE(rp.tz, 'UTC') AT TIME ZONE 'UTC')::DATE AS today
                        FROM res_company AS rc, res_users AS ru
                            LEFT JOIN res_partner AS rp ON (rp.id = ru.partner_id)
                        WHERE ru.id = 1
                    ),

                    transaction_dates AS (
                        SELECT
                            DATE_TRUNC('day', sm.date_expected2) AS date
                        FROM stock_move AS sm
                            LEFT JOIN stock_location AS sl ON (sm.location_id = sl.id)
                            LEFT JOIN stock_location AS dl ON (sm.location_dest_id = dl.id)
                            LEFT JOIN company_date AS cd ON (cd.id = sm.company_id)
                        WHERE
                            sm.state IN ('confirmed','assigned','waiting','partially_available')
                            AND sm.date_expected2 > today
                            AND (sl.usage = 'internal' OR dl.usage = 'internal')

                        UNION ALL

                        SELECT
                            today AS date
                        FROM company_date
                    ),

                    distinct_transaction_dates AS (
                        SELECT DISTINCT date
                        FROM transaction_dates
                    ),

                    current AS (
                        SELECT
                            MIN(sq.id) AS id,
                            sq.product_id,
                            DATE_TRUNC('day', today) AS date,
                            SUM(sq.quantity) AS product_qty,
                            'current'::TEXT AS transaction_type,
                            'CURRENT'::TEXT AS reference,
                            0 AS partner_id,
                            sq.location_id,
                            sq.company_id
                        FROM
                            stock_quant AS sq
                            LEFT JOIN stock_location AS sl ON (sq.location_id = sl.id)
                            LEFT JOIN company_date AS cd ON (cd.id = sq.company_id)
                        WHERE
                            sl.usage = 'internal'
                        GROUP BY sq.product_id, sq.location_id, sq.company_id, today
                    ),

                    incoming AS (
                        SELECT
                            MIN(-sm.id) AS id,
                            sm.product_id,
                            CASE WHEN sm.date_expected2 > today
                                THEN DATE_TRUNC('day', sm.date_expected2)
                                ELSE DATE_TRUNC('day', today) END
                            AS date,
                            SUM(sm.product_qty) AS product_qty,
                            CASE WHEN sm.sale_line_id IS NOT NULL THEN 'sale'
                                WHEN sm.purchase_line_id IS NOT NULL THEN 'purchase'
                                WHEN sl.usage = 'internal' THEN 'internal'
                                ELSE 'current' END AS transaction_type,
                            CASE WHEN sm.origin IS NOT NULL THEN sm.origin
                                ELSE 'UNKNOWN' END AS reference,
                            sp.partner_id,
                            sm.location_dest_id AS location_id,
                            sm.company_id
                        FROM
                            stock_move AS sm
                            LEFT JOIN stock_location AS dl ON (sm.location_dest_id = dl.id)
                            LEFT JOIN stock_location AS sl ON (sm.location_id = sl.id)
                            LEFT JOIN company_date AS cd ON (cd.id = sm.company_id)
                            LEFT JOIN stock_picking AS sp ON (sp.id = sm.picking_id)
                        WHERE
                            sm.state IN ('confirmed','assigned','waiting','partially_available')
                            AND dl.usage = 'internal'
                        GROUP BY
                            sm.date_expected2, sm.product_id, sm.purchase_line_id,
                            sm.sale_line_id, sm.origin, sp.partner_id, sm.location_dest_id,
                            sm.company_id, today, sl.usage
                    ),

                    outgoing AS (
                        SELECT
                            MIN(-500000000-sm.id) AS id,
                            sm.product_id,
                            CASE WHEN sm.date_expected2 > today
                                THEN DATE_TRUNC('day', sm.date_expected2)
                                ELSE DATE_TRUNC('day', today) END
                            AS date,
                            SUM(-(sm.product_qty)) AS product_qty,
                            CASE WHEN sm.sale_line_id IS NOT NULL THEN 'sale'
                                WHEN sm.purchase_line_id IS NOT NULL THEN 'purchase'
                                WHEN dl.usage = 'internal' THEN 'internal'
                                ELSE 'current' END AS transaction_type,
                            CASE WHEN sm.origin IS NOT NULL THEN sm.origin
                                ELSE 'UNKNOWN' END AS reference,
                            sp.partner_id,
                            sm.location_id,
                            sm.company_id
                        FROM
                            stock_move AS sm
                            LEFT JOIN stock_location AS sl ON (sm.location_id = sl.id)
                            LEFT JOIN stock_location dl ON (sm.location_dest_id = dl.id)
                            LEFT JOIN company_date AS cd ON (cd.id = sm.company_id)
                            LEFT JOIN stock_picking AS sp ON (sp.id = sm.picking_id)
                        WHERE
                            sm.state IN ('confirmed','assigned','waiting','partially_available')
                            AND sl.usage = 'internal'
                        GROUP BY
                            sm.date_expected2, sm.product_id, sm.purchase_line_id,
                            sm.sale_line_id, sm.origin, sp.partner_id, sm.location_id,
                            sm.company_id, today, dl.usage
                    ),

                    transactions AS (
                        SELECT * FROM current
                        UNION ALL
                        SELECT * FROM incoming
                        UNION ALL
                        SELECT * FROM outgoing
                    ),

                    transactions_with_dates AS (
                        SELECT
                            MIN(t.id) AS id,
                            t.product_id,
                            d.date,
                            CASE WHEN t.date = d.date
                                    THEN SUM(t.product_qty)
                                ELSE 0 END AS product_qty,
                            CASE WHEN DATE_TRUNC('week', t.date) = DATE_TRUNC('week', d.date)
                                    THEN SUM(t.product_qty)
                                ELSE NULL END AS product_qty_week,
                            CASE WHEN DATE_TRUNC('month', t.date) = DATE_TRUNC('month', d.date)
                                    THEN SUM(t.product_qty)
                                ELSE NULL END AS product_qty_month,
                            t.transaction_type,
                            t.reference,
                            t.partner_id,
                            t.location_id,
                            t.company_id
                        FROM
                            transactions AS t,
                            distinct_transaction_dates AS d
                        GROUP BY
                            t.product_id, d.date, t.date, t.transaction_type, t.reference,
                            t.partner_id, t.location_id, t.company_id
                    ),

                    final_transactions AS (
                        SELECT
                            MIN(id) AS id,
                            product_id,
                            date,
                            DATE_TRUNC('week', date) AS date_week,
                            DATE_TRUNC('month', date) AS date_month,
                            SUM(product_qty) AS quantity,
                            SUM(SUM(product_qty)) OVER (PARTITION BY product_id, transaction_type, reference, partner_id, location_id, company_id ORDER BY date) AS cumulative_quantity,
                            AVG(AVG(product_qty_week)) OVER (PARTITION BY product_id, transaction_type, reference, partner_id, location_id, company_id ORDER BY date) AS cumulative_quantity_week,
                            AVG(AVG(product_qty_month)) OVER (PARTITION BY product_id, transaction_type, reference, partner_id, location_id, company_id ORDER BY date) AS cumulative_quantity_month,
                            transaction_type,
                            reference,
                            partner_id,
                            location_id,
                            company_id
                        FROM transactions_with_dates
                        GROUP BY
                            product_id, date, transaction_type, reference,
                            partner_id, location_id, company_id
                    ),

                    cumulative_quantity_week AS (
                        SELECT
                            MIN(id) AS id,
                            MAX(date) AS date,
                            AVG(cumulative_quantity_week) AS cumulative_quantity
                        FROM final_transactions
                        GROUP BY
                            product_id, date_week, transaction_type, reference,
                            partner_id, location_id, company_id
                    ),

                    cumulative_quantity_month AS (
                        SELECT
                            MIN(id) AS id,
                            MAX(date) AS date,
                            AVG(cumulative_quantity_month) AS cumulative_quantity
                        FROM final_transactions
                        GROUP BY
                            product_id, date_month, transaction_type, reference,
                            partner_id, location_id, company_id
                    )

                SELECT
                    MIN(FINAL.id) AS id,
                    FINAL.product_id,
                    PP.default_code AS product_code,
                    FINAL.date,
                    SUM(FINAL.quantity) AS quantity,
                    SUM(FINAL.cumulative_quantity) AS cumulative_quantity,
                    SUM(CQW.cumulative_quantity) AS cumulative_quantity_week,
                    SUM(CQM.cumulative_quantity) AS cumulative_quantity_month,
                    FINAL.transaction_type,
                    FINAL.reference,
                    FINAL.partner_id,
                    FINAL.location_id,
                    FINAL.company_id,
                    SW.id AS warehouse_id,
                    PT.categ_id AS product_category_id
                FROM
                    final_transactions AS FINAL
                    LEFT JOIN stock_location AS SL ON (SL.id = FINAL.location_id)
                    LEFT JOIN stock_warehouse SW ON (SW.lot_stock_id = FINAL.location_id
                                                     OR (SL.location_id IS NOT NULL AND SW.lot_stock_id = SL.location_id))
                    LEFT JOIN product_product AS PP ON (PP.id = FINAL.product_id)
                    LEFT JOIN product_template AS PT ON (PT.id = PP.product_tmpl_id)
                    LEFT JOIN cumulative_quantity_week CQW ON (CQW.id = FINAL.id AND CQW.date = FINAL.date)
                    LEFT JOIN cumulative_quantity_month CQM ON (CQM.id = FINAL.id AND CQM.date = FINAL.date)
                GROUP BY
                    FINAL.product_id, PP.default_code, FINAL.date, FINAL.transaction_type,
                    FINAL.reference, FINAL.partner_id, FINAL.location_id, FINAL.company_id, SW.id,
                    PT.categ_id
            )
        """
        )
