import datetime
import calendar

from dateutil.rrule import rrule, MONTHLY
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from odoo import fields, _
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError


class PurchaseDashboard(http.Controller):

    # ==============================================================================================
    # Purchase Dashboard
    # ==============================================================================================

    def _compute_start_end_dates(self, start_date, end_date):
        """
        @private - Convert string format dates to datetime format
        """
        return datetime.datetime.strptime(start_date.split("T")[0], "%Y-%m-%d") + datetime.timedelta(
            days=1
        ), datetime.datetime.strptime(end_date.split("T")[0], "%Y-%m-%d") + datetime.timedelta(days=1)

    def _prepare_labels(self, start_date, end_date):
        """
        @private - Prepare labels for charts
        """
        return [
            f"{calendar.month_name[mn.month]} {mn.year}" for mn in self._compute_months_with_years(start_date, end_date)
        ]

    def _compute_months_with_years(self, start_date, end_date):
        """
        @private - compute months with years between start and end dates
        """
        return [dt for dt in rrule(MONTHLY, dtstart=start_date, until=end_date)]

    def _get_filter_where_clause(
        self, country=None, brand=None, warehouse=None, res_partner_table="irp", warehouse_table="so"
    ):
        """
        @private - get filter where clause values
        """
        filter_where_clause = ""
        if bool(country):
            country = [int(x) for x in country]
            if len(country) == 1:
                country_where_clause = f"= {country[0]}"
            else:
                country_where_clause = f"IN {tuple(country)}"
            filter_where_clause += f"AND {res_partner_table}.country_id {country_where_clause} "
        if bool(brand):
            brand = [int(x) for x in brand]
            if len(brand) == 1:
                brand_where_clause = f"= {brand[0]}"
            else:
                brand_where_clause = f"IN {tuple(brand)}"
            filter_where_clause += f"AND pt.product_breeder_id {brand_where_clause} "
        if bool(warehouse):
            warehouse = [int(x) for x in warehouse]
            if len(warehouse) == 1:
                warehouse_where_clause = f"= {warehouse[0]}"
            else:
                warehouse_where_clause = f"IN {tuple(warehouse)}"
            filter_where_clause += f"AND {warehouse_table}.warehouse_id {warehouse_where_clause} "
        return filter_where_clause

    def _get_values(self, start_date, end_date, country, brand, warehouse, **kw):
        """
        Get necessary values from sql query according to the filters
        """
        # Compute sale data
        filter_where_clause = self._get_filter_where_clause(country=country, brand=brand, warehouse=warehouse)
        filter_where_clause += f"AND so.state in ('sale', 'done') "
        query = """
            SELECT
            pt.product_breeder_id AS brand,
            sum(sol.price_total) AS sale_amount,
            sum(pt.list_price) AS cost_price,
            sum(sol.product_uom_qty) AS quantity
            FROM sale_order_line sol
            LEFT JOIN sale_order so ON so.id = sol.order_id
            LEFT JOIN res_partner irp ON irp.id = so.partner_shipping_id
            LEFT JOIN product_product pp ON pp.id = sol.product_id
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            WHERE so.date_order >= '{start_date}'
            AND so.date_order <= '{end_date}'
            {filter_where_clause}
            GROUP BY pt.product_breeder_id
            """.format(
            start_date=start_date, end_date=end_date, filter_where_clause=filter_where_clause
        )
        request.env.cr.execute(query)
        sale_query_data = request.env.cr.dictfetchall()

        # Compute purchase data
        filter_where_clause = self._get_filter_where_clause(
            country=country, brand=brand, warehouse=warehouse, res_partner_table="ppa", warehouse_table="spt"
        )
        filter_where_clause += f"AND po.state in ('purchase', 'done') "
        purchase_query = """
                    SELECT
                    pt.product_breeder_id AS brand,
                    SUM(pol.price_total) AS total_amount,
                    SUM(pol.product_qty) AS quantity
                    FROM purchase_order_line pol
                    LEFT JOIN purchase_order po ON po.id = pol.order_id
                    LEFT JOIN res_partner ppa ON ppa.id = po.partner_id
                    LEFT JOIN product_product pp ON pp.id = pol.product_id
                    LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                    LEFT JOIN stock_picking_type spt ON spt.id = po.picking_type_id
                    WHERE po.date_order >= '{start_date}'
                    AND po.date_order <= '{end_date}'
                    {filter_where_clause}
                    GROUP BY pt.product_breeder_id
                    """.format(
            start_date=start_date, end_date=end_date, filter_where_clause=filter_where_clause
        )
        request.env.cr.execute(purchase_query)
        purchase_query_data = request.env.cr.dictfetchall()

        brands = list(set([x["brand"] for x in sale_query_data] + [x["brand"] for x in purchase_query_data]))
        return sale_query_data, purchase_query_data, brands

    def _get_stock_values(self, start_date, end_date, brand, warehouse_id):
        """
        Get inventory valuation for the selected month
        """
        if type(warehouse_id) == int:
            warehouse_id = [warehouse_id]
        where_clause = self._get_filter_where_clause(brand=brand, warehouse=warehouse_id, warehouse_table="sm")
        query = """
            SELECT
            spt.code,
            sum(sm.product_uom_qty * pt.list_price) AS stock_value,
            sum(sm.product_uom_qty) AS product_qty
            FROM stock_move sm
            LEFT JOIN stock_picking_type spt ON spt.id = sm.picking_type_id
            LEFT JOIN product_product pp ON pp.id = sm.product_id
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            WHERE sm.date >= '{start_date}'
            AND sm.date <= '{end_date}'
            {where_clause}
            GROUP BY spt.code
            """.format(
            start_date=start_date, end_date=end_date, where_clause=where_clause
        )
        request.env.cr.execute(query)
        values = request.env.cr.dictfetchall()
        return values

    @http.route("/tgr/dashboard/prepare_current_stock_levels", type="json", auth="user")
    def prepare_current_stock_levels(self, start_date, end_date, country, brand, warehouse, pagination_end, *kw):
        """
        Prepare data for amount of each product sale
        """
        # start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        data = {"lines": [], "total": {}, "pg_end": 0, "all_recs": 0}
        brands = request.env["product.breeder"].sudo().search([])
        # prepare pagination
        data["all_recs"] = len(brands)
        if pagination_end == "0":
            if data["all_recs"] < 2:
                data["pg_end"] = data["all_recs"]
            else:
                data["pg_end"] = 2
        else:
            if data["all_recs"] < int(pagination_end):
                data["pg_end"] = int(pagination_end)
            else:
                data["pg_end"] = int(pagination_end)
        brands = brands[0 : data["pg_end"]]
        if bool(brand):
            brands = brands.filtered(lambda x: x.id in tuple(int(x) for x in brand))
        # warehouse_locations = request.env['stock.warehouse'].sudo().search([]).mapped('lot_stock_id.id')
        warehouse_id_obj = request.env["stock.warehouse"].sudo()
        warehouse_id = warehouse_id_obj
        if bool(warehouse):
            warehouse_id = warehouse_id_obj.browse([int(x) for x in warehouse])
            # warehouse_locations = request.env['stock.warehouse'].sudo().browse(warehouse).mapped('lot_stock_id.id')
        total_ideal_qty = 0
        total_product_on_hand = 0
        total_ideal_stock_value = 0
        product_template_obj = request.env["product.template"].sudo()
        product_product_obj = request.env["product.product"].sudo()
        for brand in brands:
            ideal_qty = 0
            product_on_hand = 0
            ideal_stock_value = 0
            # product_on_hand = sum([sum(request.env['stock.quant'].search([('product_id.product_tmpl_id', '=', x.id), ('location_id', 'in', warehouse_locations)]).mapped('quantity')) * x.list_price for x in request.env['product.template'].sudo().search([('product_breeder_id', '=', brand.id)])])
            for product in product_template_obj.search([("product_breeder_id", "=", brand.id)]):
                product_id = (
                    product_product_obj.search([("product_tmpl_id", "=", product.id)], limit=1)
                )
                product_standard_price = product_id.with_company(request.env.company.id).standard_price
                for wh in warehouse_id:
                    product_on_hand += (
                        product_id.with_context({"location": wh.lot_stock_id.id}).qty_available
                        * product_standard_price
                    )
                ideal_qty, ideal_stock_value = self._compute_ideal_inventory_value(
                    product_id, warehouse_id, product_standard_price)

            data["lines"].append(
                {
                    "brand_name": brand.breeder_name,
                    "stock_available": "{:,.2f}".format(product_on_hand),
                    "stock_value": ideal_stock_value,
                    "ideal_stock": ideal_qty,
                    "stock_value_over_ideal": ((product_on_hand - ideal_stock_value) / ideal_stock_value)
                    if ideal_stock_value != 0
                    else 0,
                }
            )
            total_ideal_qty += ideal_qty
            total_product_on_hand += product_on_hand
            total_ideal_stock_value += ideal_stock_value
        data["total"] = {
            "stock_available_total": "{:,.2f}".format(total_product_on_hand),
            "stock_value_total": total_ideal_qty,
            "ideal_stock_total": total_ideal_stock_value,
            "stock_value_over_ideal_total": (
                (total_product_on_hand - total_ideal_stock_value) / total_ideal_stock_value
            )
            if total_ideal_stock_value != 0
            else 0,
        }
        return data

    def _prepare_linechart_options(self, x_title, y_title, data):
        """
        Prepare options for linechart
        """
        data = {
            "type": "line",
            "data": data,
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "scales": {
                    "x": {
                        "stacked": False,
                        "title": {"display": True, "text": x_title},
                    },
                    "y": {"beginAtZero": True, "stacked": False, "title": {"display": True, "text": y_title}},
                },
                "plugins": {
                    "legend": {
                        "position": "top",
                    },
                    "filler": {
                        "propagate": False,
                    },
                    "title": {"display": False, "text": "Sales & Profit"},
                },
                "interaction": {
                    "intersect": False,
                },
            },
        }
        return data

    # Purchase and cogs line chart ======================================================

    def _prepare_purchase_and_cogs_linechart_data(self, start_date, end_date, country, brand, warehouse):
        """
        Generate bar chart data for given date period and given recordset
        """
        datasets = []
        dates = self._compute_months_with_years(start_date, end_date)
        data = []
        for m_d in dates:
            # Prepare monthly data
            month_start_date = m_d
            month_end_date = m_d + relativedelta(months=+1)
            sale_data, purchase_data, brands = self._get_values(
                month_start_date, month_end_date, country, brand, warehouse
            )
            data.append(
                (sum(y["total_amount"] for y in purchase_data) - sum(y["sale_amount"] for y in sale_data))
                / sum(y["sale_amount"] for y in sale_data)
                if sum(y["sale_amount"] for y in sale_data) != 0
                else 0
            )
        datasets.extend(
            [
                {
                    "label": "Purchases / COGS",
                    "data": data,
                    "borderColor": "rgb(255, 99, 132)",
                    "backgroundColor": "rgb(255, 99, 132, 0.3)",
                }
            ]
        )
        return datasets

    @http.route("/tgr/dashboard/get_purchase_and_cogs_data", type="json", auth="user")
    def get_purchase_and_cogs_data(self, start_date, end_date, country, brand, warehouse, *kw):
        """
        Prepare purchase and cogs line chart data
        """
        start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        data = {
            "labels": self._prepare_labels(start_date, end_date),
            "datasets": self._prepare_purchase_and_cogs_linechart_data(start_date, end_date, country, brand, warehouse),
        }
        x_title = "Month"
        return self._prepare_linechart_options(x_title, "Purchase / COGS", data)

    # Stock value Bar chart====================================================================================

    def _prepare_stock_value_bar_chart_data(self, start_date, end_date, country, brand, warehouse):
        """
        Generate bar chart data for stock value
        """
        # --------------------
        datasets = []
        dates = self._compute_months_with_years(start_date, end_date)
        warehouse_ids = request.env["stock.warehouse"].sudo().search([])
        if bool(warehouse):
            warehouse_ids = warehouse_ids.filtered(lambda x: x.id in tuple(warehouse))
        for warehouse_id in warehouse_ids:
            data = []
            for m_d in dates:
                # Prepare monthly data
                month_start_date = m_d
                month_end_date = m_d + relativedelta(months=+1)
                stock_values = self._get_stock_values(month_start_date, month_end_date, brand, warehouse_id.id)
                incoming = sum(
                    x["stock_value"] for x in stock_values if x["code"] == "incoming" and x["stock_value"] is not None
                )
                outgoing = sum(
                    x["stock_value"] for x in stock_values if x["code"] == "outgoing" and x["stock_value"] is not None
                )
                stock_value = incoming - outgoing
                data.append(stock_value)
            datasets.append(
                {
                    "label": warehouse_id.name,
                    "data": data,
                    "backgroundColor": warehouse_id.dashboard_color,
                    "borderColor": warehouse_id.dashboard_color,
                    "borderWidth": 1,
                    "borderRadius": 7,
                    "order": 1,
                    "stack": "1",
                    "datalabels": {
                        "align": "top",
                        "anchor": "end",
                    },
                }
            )
        return datasets

    def _prepare_barchart_options(self, x_title, y_title, data, legend_position=False):
        """
        Prepare options for barchart
        """
        data = {
            "type": "bar",
            "data": data,
            "options": {
                "scales": {
                    "x": {
                        "stacked": True,
                        "title": {"display": True, "text": x_title},
                    },
                    "y": {"beginAtZero": True, "stacked": True, "title": {"display": True, "text": y_title}},
                },
                # Tooltip option
                "interaction": {"mode": "nearest"},
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "display": True,
                        "labels": {
                            "color": "rgb(51, 51, 51)",
                        },
                        "position": "top" if not legend_position else legend_position,
                    },
                    "title": {"position": "bottom", "display": True, "fullSize": True},
                    "datalabels": {
                        "color": "rgb(102, 102, 102)",
                        "font": {"weight": "bold"},
                    },
                },
            },
        }
        return data

    @http.route("/tgr/dashboard/get_stock_value_barchart_data", type="json", auth="user")
    def get_stock_value_barchart_data(self, start_date, end_date, country, brand, warehouse, *kw):
        """
        Prepare stock value bar chart data
        """
        start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        data = {
            "labels": self._prepare_labels(start_date, end_date),
            "datasets": self._prepare_stock_value_bar_chart_data(start_date, end_date, country, brand, warehouse),
        }
        x_title = "Months"
        return self._prepare_barchart_options(x_title, "Stock Value €", data, legend_position="right")

    # Sell through rate line chart ===============================================================

    def _prepare_sell_through_rate_linechart_data(self, start_date, end_date, country, brand, warehouse):
        """
        Generate line chart data for given date period and given recordset
        """
        datasets = []
        dates = self._compute_months_with_years(start_date, end_date)
        data = []
        # profit_data = []
        for m_d in dates:
            # Prepare monthly data
            month_start_date = m_d
            month_end_date = m_d + relativedelta(months=+1)
            sale_data, purchase_data, brands = self._get_values(
                month_start_date, month_end_date, country, brand, warehouse
            )
            data.append(
                ((sum(x["quantity"] for x in sale_data) / sum(x["quantity"] for x in purchase_data)) * 100)
                if sum(x["quantity"] for x in purchase_data) != 0
                else 0
            )
        datasets.extend(
            [
                {
                    "label": "Sell Through Rate",
                    "data": data,
                    "borderColor": "rgb(255, 99, 132)",
                    "backgroundColor": "rgb(255, 99, 132, 0.3)",
                }
            ]
        )
        return datasets

    @http.route("/tgr/dashboard/get_sell_though_rate_line_chart_data", type="json", auth="user")
    def get_sell_though_rate_line_chart_data(self, start_date, end_date, country, brand, warehouse, *kw):
        """
        Prepare sell through rate line chart data
        """
        start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        data = {
            "labels": self._prepare_labels(start_date, end_date),
            "datasets": self._prepare_sell_through_rate_linechart_data(start_date, end_date, country, brand, warehouse),
        }
        x_title = "Month"
        return self._prepare_linechart_options(x_title, "Sell Through Rate %", data)

    # Sales of brand table ==============================================================================

    # Get where clause for sales of brand filters
    def _get_sob_filter_where_clause(
        self, filters, res_partner_table="irp", warehouse_table="so", warehouse=True, country=True
    ):
        """
        @private - get filter where clause values
        """
        filter_where_clause = ""

        if filters.get("sob_brand", False) and bool(filters["sob_brand"]):
            brand = [int(x) for x in filters["sob_brand"]]
            if len(brand) == 1:
                brand_where_clause = f"= {brand[0]}"
            else:
                brand_where_clause = f"IN {tuple(brand)}"
            filter_where_clause += f"AND pt.product_breeder_id {brand_where_clause} "

        if filters.get("sob_sex", False) and bool(filters["sob_sex"]):
            sex = [int(x) for x in filters["sob_sex"]]
            if len(sex) == 1:
                sex_where_clause = f"= {sex[0]}"
            else:
                sex_where_clause = f"IN {tuple(sex)}"
            filter_where_clause += f"AND pt.product_sex_id {sex_where_clause} "

        if filters.get("sob_flowering_type", False) and bool(filters["sob_flowering_type"]):
            flowering_type = [int(x) for x in filters["sob_flowering_type"]]
            if len(flowering_type) == 1:
                flowering_type_where_clause = f"= {flowering_type[0]}"
            else:
                flowering_type_where_clause = f"IN {tuple(flowering_type)}"
            filter_where_clause += f"AND pt.flower_type_id {flowering_type_where_clause} "

        if filters.get("sob_product_category", False) and bool(filters["sob_product_category"]):
            product_category = [int(x) for x in filters["sob_product_category"]]
            if len(product_category) == 1:
                product_category_where_clause = f"= {product_category[0]}"
            else:
                product_category_where_clause = f"IN {tuple(product_category)}"
            filter_where_clause += f"AND pt.categ_id {product_category_where_clause} "

        if warehouse and filters.get("sob_warehouse", False) and bool(filters["sob_warehouse"]):
            warehouse = [int(x) for x in filters["sob_warehouse"]]
            if len(warehouse) == 1:
                warehouse_where_clause = f"= {warehouse[0]}"
            else:
                warehouse_where_clause = f"IN {tuple(warehouse)}"
            filter_where_clause += f"AND {warehouse_table}.warehouse_id {warehouse_where_clause} "

        if country and filters.get("sob_country", False) and bool(filters["sob_country"]):
            country = [int(x) for x in filters["sob_country"]]
            if len(country) == 1:
                country_where_clause = f"= {country[0]}"
            else:
                country_where_clause = f"IN {tuple(country)}"
            filter_where_clause += f"AND {res_partner_table}.country_id {country_where_clause} "
        return filter_where_clause

    # Get sales of brand table values
    def _get_sales_of_brand_table_values(self, start_date, end_date, sob_data):
        """
        @Override - Get sales of brand related table values
        """
        create_date_start, create_date_end = self._get_sob_filter_start_end_dates(
            sob_data, "sob_create_date_start", "sob_create_date_end"
        )
        # Compute sale data
        filter_where_clause = self._get_sob_filter_where_clause(filters=sob_data, warehouse=False, country=False)
        # filter_where_clause += f'AND so.state in (\'sale\', \'done\') '
        query = """
            SELECT
            pt.product_breeder_id AS brand,
            pt.default_code AS sku,
            pt.name AS product_name,
            pt.pack_size_desc AS pack_size,
            pb.breeder_name AS brand,
            ps.product_sex_des AS sex,
            pp.id AS product_id,
            ft.flower_type_des AS flower_type,
            pc.name AS category
            FROM product_product pp
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN product_sex ps ON ps.id = pt.product_sex_id
            LEFT JOIN product_breeder pb ON pb.id = pt.product_breeder_id
            LEFT JOIN flower_type ft ON ft.id = pt.flower_type_id
            LEFT JOIN product_category pc ON pc.id = pt.categ_id
            WHERE pt.create_date >= '{create_date_start}'
            AND pt.create_date <= '{create_date_end}'
            --AND pt.id = 204131  -- TODO Remove line
            {filter_where_clause}
            GROUP BY
            pt.product_breeder_id,
            pt.default_code,
            pt.name,
            pt.pack_size_desc,
            pb.breeder_name,
            ps.product_sex_des,
            ft.flower_type_des,
            pc.name,
            pp.id
            """.format(
            start_date=start_date,
            end_date=end_date,
            create_date_start=create_date_start,
            create_date_end=create_date_end,
            filter_where_clause=filter_where_clause,
        )
        request.env.cr.execute(query)
        sale_query_data = request.env.cr.dictfetchall()
        return sale_query_data

    def _get_sob_filter_start_end_dates(self, sob_data, start_date_key, end_date_key):
        start_date = sob_data.get(start_date_key, False)
        end_date = sob_data.get(end_date_key, False)
        if not start_date or not end_date:
            raise ValidationError(_("Something went wrong. Please reload the current window."))
        return self._compute_start_end_dates(start_date, end_date)

    def _compute_ideal_inventory_value(self, product_id, warehouse_ids, product_standard_price):
        """
        @private - Get ideal inventory value for the sales of brand table
        """
        today_date = fields.Date.today()
        # total_delivered_quantity = 0
        # for i in range(12, 0, -1):
        #     start_period_date = today_date - timedelta(days=i * 7)
        #     end_period_date = start_period_date + timedelta(days=6)
        #     domain = [
        #         ("product_id", "=", product_id.id),
        #         ("order_id.state", "in", ("done", "sale")),
        #         ("order_id.date_order", ">=", start_period_date),
        #         ("order_id.date_order", "<=", end_period_date),
        #     ]
        #     if warehouse_ids:
        #         domain.extend([("order_id.warehouse_id", "in", warehouse_ids.ids)])
        #     sale_line_ids = sol_obj.search_read(domain, ["qty_delivered"])
        #     qty_delivered = round(sum(x["qty_delivered"] for x in sale_line_ids), 2)
        #     total_delivered_quantity += qty_delivered

        where_clause = "pp.id = {product_id} AND so.state in ('sale', 'done') ".format(product_id=product_id.id)
        if warehouse_ids:
            where_clause += "AND so.warehouse_id IN {warehouse_ids}".format(warehouse_ids=tuple(warehouse_ids.ids))
        where_clause += " AND ("
        first_period = True
        for i in range(12, 0, -1):
            start_period_date = today_date - timedelta(days=i * 7)
            end_period_date = start_period_date + timedelta(days=6)
            if first_period:
                wr_clus = " (so.date_order >= '{start_period_date}' AND so.date_order <= '{end_period_date}')".format(
                    start_period_date=start_period_date,
                    end_period_date=end_period_date
                )
                first_period = False
            else:
                wr_clus = "OR (so.date_order >= '{start_period_date}' AND so.date_order <= '{end_period_date}')".format(
                    start_period_date=start_period_date,
                    end_period_date=end_period_date
                )
            where_clause += wr_clus

        where_clause += ")"
        query = ("SELECT SUM(qty_delivered) AS total_delivered_quantity "
                 "FROM sale_order_line sol "
                 "LEFT JOIN sale_order so ON so.id = sol.order_id "
                 "LEFT JOIN product_product pp ON pp.id = sol.product_id "
                 "WHERE {where_clause}".format(
            where_clause=where_clause
        ))

        request.env.cr.execute(query)
        query_data = request.env.cr.dictfetchall()
        quantity_data = query_data[0]
        total_delivered_quantity = quantity_data and quantity_data.get('total_delivered_quantity', False) or 0

        average = total_delivered_quantity / 12
        ideal_qty = round(average * 5)
        return ideal_qty, ideal_qty * product_standard_price

    def _get_calculation_values(self, start_date, end_date, sob_data, product_id, warehouse_ids=False):
        create_date_start, create_date_end = self._get_sob_filter_start_end_dates(
            sob_data, "sob_create_date_start", "sob_create_date_end"
        )
        # Get inventory value
        if not warehouse_ids:
            warehouse_ids = request.env["stock.warehouse"].sudo().search([])
        else:
            warehouse_ids = request.env["stock.warehouse"].sudo().browse(warehouse_ids)
        location_ids = warehouse_ids.mapped("lot_stock_id").ids
        where_clause = f" product_id = {product_id}"
        if len(location_ids) == 1:
            where_clause += f" AND location_id = {location_ids[0]}"
        elif len(location_ids) > 1:
            where_clause += f" AND location_id IN {tuple(location_ids)}"
        query = """
        SELECT SUM(quantity) AS on_hand
        FROM stock_quant
        WHERE{where_clause}
        """.format(
            where_clause=where_clause
        )
        request.env.cr.execute(query)
        on_hand_quantity = request.env.cr.dictfetchall()
        on_hand_quantity = (
            (on_hand_quantity[0]["on_hand"] if on_hand_quantity[0]["on_hand"] is not None else 0.00)
            if on_hand_quantity
            else 0.00
        )
        product_obj_id = request.env["product.product"].sudo().browse(product_id)
        product_standard_price = product_obj_id.with_company(request.env.company.id).standard_price
        inventory_value = on_hand_quantity * product_standard_price
        ideal_qty, ideal_inventory_value = self._compute_ideal_inventory_value(
            product_obj_id, warehouse_ids, product_standard_price)
        inventory_value_vs_ideal_value = ideal_inventory_value and ((inventory_value - ideal_inventory_value) / ideal_inventory_value) * 100 or 0.00
        # Sale values
        filter_sale_where_clause = self._get_sob_filter_where_clause(filters=sob_data)
        filter_sale_where_clause += f"AND so.state in ('sale', 'done') "
        sale_query = """
            SELECT
            sum(sol.price_total) AS sale_amount,
            sum(pt.list_price) AS cost_price,
            sum(sol.product_uom_qty) AS quantity
            FROM sale_order_line sol
            LEFT JOIN sale_order so ON so.id = sol.order_id
            LEFT JOIN product_product pp ON pp.id = sol.product_id
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN stock_warehouse sw ON sw.id = so.warehouse_id
            LEFT JOIN res_partner irp ON irp.id = so.partner_id
            --WHERE so.date_order >= '{start_date}'
            --AND so.date_order <= '{end_date}'
            WHERE pp.id = {product_id}
            {filter_where_clause}
            """.format(
            start_date=start_date,
            end_date=end_date,
            product_id=product_id,
            create_date_start=create_date_start,
            create_date_end=create_date_end,
            filter_where_clause=filter_sale_where_clause,
        )
        request.env.cr.execute(sale_query)
        sale_query_data = request.env.cr.dictfetchall()
        sale_data = sale_query_data[0]
        sale_data = {
            "sale_amount": sale_data["sale_amount"] if sale_data["sale_amount"] is not None else 0.00,
            "quantity": sale_data["quantity"] if sale_data["quantity"] is not None else 0.00,
        }
        # Purchase values
        filter_where_clause = self._get_sob_filter_where_clause(filters=sob_data, warehouse_table="spt")
        filter_where_clause += f"AND po.state in ('purchase', 'done') AND pp.id = {product_id}"
        purchase_query = """
            SELECT
            SUM(pol.price_total) AS total_amount,
            SUM(pol.product_qty) AS quantity
            FROM purchase_order_line pol
            LEFT JOIN purchase_order po ON po.id = pol.order_id
            LEFT JOIN product_product pp ON pp.id = pol.product_id
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN stock_picking_type spt ON spt.id = po.picking_type_id
            LEFT JOIN product_sex ps ON ps.id = pt.product_sex_id
            LEFT JOIN flower_type ft ON ft.id = pt.flower_type_id
            LEFT JOIN product_category pc ON pc.id = pt.categ_id
            LEFT JOIN stock_warehouse sw ON sw.id = spt.warehouse_id
            LEFT JOIN res_partner irp ON irp.id = po.partner_id
            -- WHERE po.date_order >= '{start_date}'
            -- AND po.date_order <= '{end_date}'
            WHERE pp.id = {product_id}
            {filter_where_clause}
            """.format(
            start_date=start_date, end_date=end_date, product_id=product_id, filter_where_clause=filter_where_clause
        )
        request.env.cr.execute(purchase_query)
        purchase_values = request.env.cr.dictfetchall()
        # purchase_total = (
        #     (purchase_values[0]["total_amount"] if purchase_values[0]["total_amount"] is not None else 0.00)
        #     if purchase_values
        #     else 0.00
        # )
        purchase_total_qty = (
            (purchase_values[0]["quantity"] if purchase_values[0]["quantity"] is not None else 0.00)
            if purchase_values
            else 0.00
        )
        purchase_total_val = purchase_total_qty * product_standard_price
        # total_purchases = product_obj_id.with_company(request.env.company.id).standard_price * purchase_total
        total_sales = sale_data.get("sale_amount", 0.00)
        total_profit = total_sales - (sale_data.get("quantity", 0.00) * product_standard_price)
        total_sales_qty = sale_data.get("quantity", 0.00)
        cost_of_sale = sale_data.get("quantity", 0.00) * product_standard_price
        purchase_v_cost_of_sales = ((purchase_total_val - cost_of_sale) / purchase_total_val) * 100 if purchase_total_val > 0 else 0.00
        profit_margin = ((total_sales - cost_of_sale) / total_sales) * 100 if total_sales > 0 else 0.00
        sell_through = ((total_sales_qty / purchase_total_qty) * 100) if purchase_total_qty > 0 else 0.00
        abc_classification = 0.00  # FIXME
        company_id = False
        if sob_data.get('sob_company'):
            company_id = int(sob_data.get('sob_company')[0])
        if company_id:
        # Get last sale order date
            last_sale_order_date_query = """
                SELECT
                so.date_order as last_sale_order_date
                FROM sale_order_line sol
                LEFT JOIN sale_order so ON so.id = sol.order_id
                LEFT JOIN product_product pp ON pp.id = sol.product_id
                LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                LEFT JOIN stock_warehouse sw ON sw.id = so.warehouse_id
                LEFT JOIN res_partner irp ON irp.id = so.partner_id
                --WHERE so.date_order >= '{start_date}'
                --AND so.date_order <= '{end_date}'
                WHERE pp.id = {product_id}
                {filter_where_clause}
                AND so.company_id = {company_id}
                GROUP BY so.date_order
                ORDER BY so.date_order DESC
                LIMIT 1
                """.format(
                start_date=start_date,
                end_date=end_date,
                product_id=product_id,
                filter_where_clause=filter_sale_where_clause,
                company_id=company_id
            )
        else:
            last_sale_order_date_query = """
                SELECT
                so.date_order as last_sale_order_date
                FROM sale_order_line sol
                LEFT JOIN sale_order so ON so.id = sol.order_id
                LEFT JOIN product_product pp ON pp.id = sol.product_id
                LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                LEFT JOIN stock_warehouse sw ON sw.id = so.warehouse_id
                LEFT JOIN res_partner irp ON irp.id = so.partner_id
                --WHERE so.date_order >= '{start_date}'
                --AND so.date_order <= '{end_date}'
                WHERE pp.id = {product_id}
                {filter_where_clause}
                GROUP BY so.date_order
                ORDER BY so.date_order DESC
                LIMIT 1
                """.format(
                start_date=start_date,
                end_date=end_date,
                product_id=product_id,
                filter_where_clause=filter_sale_where_clause,
            )
        request.env.cr.execute(last_sale_order_date_query)
        try:
            last_sale_order_date = request.env.cr.dictfetchall()[0]["last_sale_order_date"]
        except:
            last_sale_order_date = None

        # Get last receipt date
        if company_id:
            last_receipt_date_query = """
                SELECT
                po.effective_date as last_receipt_date
                FROM purchase_order_line pol
                LEFT JOIN purchase_order po ON po.id = pol.order_id
                LEFT JOIN product_product pp ON pp.id = pol.product_id
                LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                LEFT JOIN stock_picking_type spt ON spt.id = po.picking_type_id
                LEFT JOIN product_sex ps ON ps.id = pt.product_sex_id
                LEFT JOIN flower_type ft ON ft.id = pt.flower_type_id
                LEFT JOIN product_category pc ON pc.id = pt.categ_id
                LEFT JOIN stock_warehouse sw ON sw.id = spt.warehouse_id
                LEFT JOIN res_partner irp ON irp.id = po.partner_id
                -- WHERE po.date_order >= '{start_date}'
                -- AND po.date_order <= '{end_date}'
                WHERE pp.id = {product_id}
                {filter_where_clause}
                AND po.company_id = {company_id}
                GROUP BY po.effective_date
                ORDER BY po.effective_date DESC
                LIMIT 1
                """.format(
                start_date=start_date, end_date=end_date, product_id=product_id, filter_where_clause=filter_where_clause,company_id=company_id
            )
        else:
            last_receipt_date_query = """
                SELECT
                po.effective_date as last_receipt_date
                FROM purchase_order_line pol
                LEFT JOIN purchase_order po ON po.id = pol.order_id
                LEFT JOIN product_product pp ON pp.id = pol.product_id
                LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                LEFT JOIN stock_picking_type spt ON spt.id = po.picking_type_id
                LEFT JOIN product_sex ps ON ps.id = pt.product_sex_id
                LEFT JOIN flower_type ft ON ft.id = pt.flower_type_id
                LEFT JOIN product_category pc ON pc.id = pt.categ_id
                LEFT JOIN stock_warehouse sw ON sw.id = spt.warehouse_id
                LEFT JOIN res_partner irp ON irp.id = po.partner_id
                -- WHERE po.date_order >= '{start_date}'
                -- AND po.date_order <= '{end_date}'
                WHERE pp.id = {product_id}
                {filter_where_clause}
                GROUP BY po.effective_date
                ORDER BY po.effective_date DESC
                LIMIT 1
                """.format(
                start_date=start_date, end_date=end_date, product_id=product_id, filter_where_clause=filter_where_clause
            )
        request.env.cr.execute(last_receipt_date_query)
        try:
            last_receipt_or_kit_assembly_date = request.env.cr.dictfetchall()[0]["last_receipt_date"]
        except:
            last_receipt_or_kit_assembly_date = None

        data = {
            "inventory_value": inventory_value,
            "ideal_inventory_value": ideal_inventory_value,
            "inv_value_v_ideal_value": inventory_value_vs_ideal_value,
            "total_purchases": purchase_total_val,
            "total_purchase_qty": purchase_total_qty,
            "total_sales": total_sales,
            "total_profit": total_profit,
            "total_sales_qty": total_sales_qty,
            "cost_of_sales": cost_of_sale,
            "purchase_vs_cost_of_sales": purchase_v_cost_of_sales,
            "profit_margin": profit_margin,
            "sell_through": sell_through,
            "abc_classification": abc_classification,
        }

        return last_sale_order_date, last_receipt_or_kit_assembly_date, data

    @http.route("/tgr/dashboard/prepare_sales_of_brand_data", type="json", auth="user")
    def prepare_sales_of_brand_data(self, start_date, end_date, country, brand, warehouse,sob_data, *kw):
        """
        Prepare data for sales of brand data table
        """
        start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        data = {"lines": [], "total": {}, "pg_end": 0, "all_recs": 0}
        sale_query_data = self._get_sales_of_brand_table_values(start_date, end_date, sob_data)
        sale_query_data.sort(key=lambda x: x["product_name"])
        data["all_recs"] = len(sale_query_data)
        if sob_data["pagination_end"] == "0":
            if data["all_recs"] < 10:
                data["pg_end"] = data["all_recs"]
            else:
                data["pg_end"] = 10
        else:
            if data["all_recs"] < int(sob_data["pagination_end"]):
                data["pg_end"] = int(sob_data["pagination_end"])
            else:
                data["pg_end"] = int(sob_data["pagination_end"])
        sale_query_data = sale_query_data[0 : data["pg_end"]]
        total_values = {
            "total_inv_val": [],
            "total_ideal_inv_val": [],
            "total_inv_val_v_ideal_inv_val": [],
            "total_purchases": [],
            "total_purchase_qty": [],
            "total_sales": [],
            "total_profit": [],
            "total_sales_qty": [],
            "total_cost_of_sales": [],
            "total_purchases_vs_cost_of_sales": [],
            "profit_margin_total": [],
            "sell_through_total": [],
            "total_abc_classification": [],
        }

        product_product_obj = request.env["product.product"].sudo()
        for line in sale_query_data:
            last_sale_date, last_receipt_or_kit_assembly_date, line_data = self._get_calculation_values(
                start_date, end_date, sob_data, line["product_id"], sob_data['sob_warehouse'] and sob_data['sob_warehouse'] or warehouse
                and sob_data['sob_company']
            )
            product_id = product_product_obj.browse(line["product_id"])
            data["lines"].append(
                {
                    "brand_name": line["brand"] if line["brand"] is not None else "No Brand",
                    "sku": line["sku"],
                    "name": line["product_name"],
                    "inventory_value": "{:,.2f}".format(line_data["inventory_value"]),
                    "ideal_inventory_value": "{:,.2f}".format(line_data["ideal_inventory_value"]),
                    "inv_value_v_ideal_value": "{:,.2f}".format(line_data["inv_value_v_ideal_value"]),
                    "total_purchases": "{:,.2f}".format(line_data["total_purchases"]),
                    "total_purchase_qty": "{:,.2f}".format(line_data["total_purchase_qty"]),
                    "total_sales": "{:,.2f}".format(line_data["total_sales"]),
                    "total_profit": "{:,.2f}".format(line_data["total_profit"]),
                    "total_sales_qty": "{:,.2f}".format(line_data["total_sales_qty"]),
                    "cost_of_sales": "{:,.2f}".format(line_data["cost_of_sales"]),
                    "purchase_vs_cost_of_sales": "{:,.2f}".format(line_data["purchase_vs_cost_of_sales"]),
                    "profit_margin": "{:,.2f}".format(line_data["profit_margin"]),
                    "sell_through": "{:,.2f}".format(line_data["sell_through"]),
                    "abc_classification": "{:,.2f}".format(line_data["abc_classification"]),
                    "pack_size": line["pack_size"] if line["pack_size"] is not None else '',
                    "sex": line["sex"] if line["sex"] is not None else '',
                    "flower_type": line["flower_type"] if line["flower_type"] is not None else '',
                    "create_date": product_id.create_date.strftime("%Y-%m-%d %H:%M"),
                    "last_sale_date": last_sale_date and last_sale_date.strftime("%Y-%m-%d %H:%M") or '',
                    "last_receipt_or_kit_assembly_date": last_receipt_or_kit_assembly_date and (last_receipt_or_kit_assembly_date + timedelta(hours=5, minutes=30, seconds=29)).strftime("%Y-%m-%d %H:%M") or '',
                    "product_group_category": line["category"],
                    # "total_purchase_qty": line_data["total_purchase_qty"] and line_data["total_purchase_qty"] or 0.00
                }
            )
            total_values["total_inv_val"].append(line_data["inventory_value"])
            total_values["total_ideal_inv_val"].append(line_data["ideal_inventory_value"])
            total_values["total_inv_val_v_ideal_inv_val"].append(line_data["inv_value_v_ideal_value"])
            total_values["total_purchases"].append(line_data["total_purchases"])
            total_values["total_purchase_qty"].append(line_data["total_purchase_qty"])
            total_values["total_sales"].append(line_data["total_sales"])
            total_values["total_profit"].append(line_data["total_profit"])
            total_values["total_sales_qty"].append(line_data["total_sales_qty"])
            total_values["total_cost_of_sales"].append(line_data["cost_of_sales"])
            total_values["total_purchases_vs_cost_of_sales"].append(line_data["purchase_vs_cost_of_sales"])
            total_values["profit_margin_total"].append(line_data["profit_margin"])
            total_values["sell_through_total"].append(line_data["sell_through"])
            total_values["total_abc_classification"].append(line_data["abc_classification"])
        data["total"] = {
            "total_inv_val": "{:,.2f}".format(sum(total_values["total_inv_val"])),
            "total_ideal_inv_val": "{:,.2f}".format(sum(total_values["total_ideal_inv_val"])),
            "total_inv_val_v_ideal_inv_val": "{:,.2f}".format(sum(total_values["total_inv_val_v_ideal_inv_val"])),
            "total_purchases": "{:,.2f}".format(sum(total_values["total_purchases"])),
            "total_purchase_qty" : "{:,.2f}".format(sum(total_values["total_purchase_qty"])),
            "total_sales": "{:,.2f}".format(sum(total_values["total_sales"])),
            "total_profit": "{:,.2f}".format(sum(total_values["total_profit"])),
            "total_sales_qty": "{:,.2f}".format(sum(total_values["total_sales_qty"])),
            "total_cost_of_sales": "{:,.2f}".format(sum(total_values["total_cost_of_sales"])),
            "total_purchases_vs_cost_of_sales": "{:,.2f}".format(
                sum(total_values["total_purchases_vs_cost_of_sales"])
            ),
            "profit_margin_total": "{:,.2f}".format(sum(total_values["profit_margin_total"])),
            "sell_through_total": "{:,.2f}".format(sum(total_values["sell_through_total"])),
            "total_abc_classification": "{:,.2f}".format(sum(total_values["total_abc_classification"])),
        }
        return data

    # Seedsman sales by product bar chart =======================================================================

    def _prepare_seedsman_sales_by_product_bar_chart_data(self, start_date, end_date, country, brand, warehouse):
        """
        @private - return datasets for seedman sales by product barchart
        """
        filter_where_clause = self._get_filter_where_clause(country=country, brand=brand, warehouse=warehouse)
        filter_where_clause += f"AND so.state in ('sale', 'done') "
        query = """SELECT pt.name, sum(product_uom_qty) as qty from sale_order_line sol
                    LEFT JOIN product_product pp ON pp.id = sol.product_id
                    LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                    LEFT JOIN product_breeder pb ON pb.id = pt.product_breeder_id
                    LEFT JOIN sale_order so ON so.id = sol.order_id
                    LEFT JOIN res_partner irp ON irp.id = so.partner_shipping_id
                    WHERE pb.breeder_name = 'Seedsman'
                    AND so.date_order >= '{start_date}'
                    AND so.date_order <= '{end_date}'
                    {filter_where_clause}
                    GROUP BY pb.breeder_name, pt.name
                    """.format(
            start_date=start_date, end_date=end_date, filter_where_clause=filter_where_clause
        )
        request.env.cr.execute(query)
        data = request.env.cr.dictfetchall()
        return [x["name"] for x in data], [
            {
                "axis": "y",
                "label": "Seedsman Sales",
                "data": [x["qty"] for x in data],
                "fill": False,
                "backgroundColor": [
                    "rgba(75, 192, 192, 0.2)",
                ],
                "borderColor": [
                    "rgb(75, 192, 192)",
                ],
                "borderWidth": 1,
            }
        ]

    def _prepare_horizontal_barchart_options(self, data):
        """
        @private - return options for horizontal barchart
        """
        return {
            "type": "bar",
            "data": data,
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "indexAxis": "y",
            },
        }

    @http.route("/tgr/dashboard/get_seedsman_sales_by_product_barchart_data", type="json", auth="user")
    def get_seedsman_sales_by_product_barchart_data(self, start_date, end_date, country, brand, warehouse, *kw):
        """
        Prepare seedsman sales by product barchart data
        """
        start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        labels, datasets = self._prepare_seedsman_sales_by_product_bar_chart_data(
            start_date, end_date, country, brand, warehouse
        )
        data = {
            "labels": labels,
            "datasets": datasets,
        }
        return self._prepare_horizontal_barchart_options(data)

    @http.route("/tgr/dashboard/get_sob_filter_values", type="json", auth="user")
    def get_sob_filter_values(self, purchase=False, *kw):
        """
        Prepare filtering values for filter inputs in sales of brand table
        """
        return {
            "brands": [
                {
                    "id": x.id,
                    "name": x.breeder_name or "Unspecified",
                }
                for x in request.env["product.breeder"].sudo().search([]).sorted(lambda m: m.breeder_name)
            ],
            "abc_classification": [
                {
                    "id": x.lower(),
                    "name": x,
                }
                for x in ["A", "B", "C"]
            ],
            "sex": [
                {
                    "id": x.id,
                    "name": x.product_sex_des or "Unspecified",
                }
                for x in request.env["product.sex"].sudo().search([]).sorted(lambda m: m.product_sex_des)
            ],
            "flowering_type": [
                {
                    "id": x.id,
                    "name": x.flower_type_des or "Unspecified",
                }
                for x in request.env["flower.type"].sudo().search([]).sorted(lambda m: m.flower_type_des)
            ],
            "product_tag": [
                {
                    "id": x.id,
                    "name": x.name,
                }
                for x in request.env["product.tag"].sudo().search([]).sorted(lambda m: m.name)
            ],
            "product_categ": [
                {
                    "id": x.id,
                    "name": x.name,
                }
                for x in request.env["product.category"].sudo().search([]).sorted(lambda m: m.name)
            ],
            "product_segment": [
                {
                    "id": x.id,
                    "name": x.name or "Unspecified",
                }
                for x in []
            ],
            "warehouses": [
                {
                    "id": x.id,
                    "name": x.name,
                }
                for x in request.env["stock.warehouse"].sudo().search([]).sorted(lambda m: m.name)
            ],
            "website": [
                {
                    "id": x.id,
                    "name": x.name,
                }
                for x in request.env["magento.website"].sudo().search([]).sorted(lambda m: m.name)
            ],
            "region": [
                {
                    "id": x.id,
                    "name": x.name or "Unspecified",
                }
                for x in []
            ],
            "countries": [
                {
                    "id": x.id,
                    "name": x.name or "Unspecified",
                }
                for x in request.env["res.country"].sudo().search([]).sorted(lambda m: m.name)
            ],
            "company": [
                {
                    "id": x.id,
                    "name": x.name or "Unspecified",
                }
                for x in request.env["res.company"].sudo().search([]).sorted(lambda m: m.name)
            ],
        }
