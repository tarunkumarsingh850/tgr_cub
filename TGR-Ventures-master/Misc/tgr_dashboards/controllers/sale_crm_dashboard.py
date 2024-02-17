import datetime
import calendar

from dateutil.rrule import rrule, MONTHLY
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from odoo import _
from odoo import http
from odoo.http import request


class TgrSaleDashboard(http.Controller):
    @http.route("/tgr/dashboard/get_summary_sale_view_action", type="json", auth="user")
    def get_summary_sale_view_action(
        self, start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers=None, *kw
    ):
        """
        Get sale order view action for sale summary records
        """
        data = self._get_sale_orders(start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers)
        order_ids = list({x["order_id"] for x in data})
        return {
            "name": _("Sale Orders"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "view_mode": "tree,form",
            "views": [[False, "list"], [False, "form"]],
            "target": "current",
            "domain": [("id", "in", order_ids)],
            "context": {},
        }

    @http.route("/tgr/dashboard/get_filter_values", type="json", auth="user")
    def get_filter_values(self, purchase=False, *kw):
        """
        Prepare filtering values for filter inputs
        """
        breeder_domain = []
        if not purchase:
            breeder_domain.extend([("is_visible_in_dashboard", "=", True)])
        return {
            "countries": [
                {
                    "id": x.id,
                    "name": x.name or "Unspecified",
                }
                for x in request.env["res.country"].sudo().search([]).sorted(lambda m: m.name)
            ],
            "salespersons": [
                {
                    "id": x.id,
                    "name": x.name or "Unspecified",
                }
                for x in request.env["res.users"].sudo().search([]).sorted(lambda m: m.name)
            ],
            "warehouses": [
                {
                    "id": x.id,
                    "name": x.name or "Unspecified",
                }
                for x in request.env["stock.warehouse"].sudo().search([]).sorted(lambda m: m.name)
            ],
            "brands": [
                {
                    "id": x.id,
                    "name": x.breeder_name or "Unspecified",
                }
                for x in request.env["product.breeder"].sudo().search(breeder_domain).sorted(lambda m: m.breeder_name)
            ],
            "wholesale_customers": [
                {
                    "id": x.id,
                    "name": x.name or "Unspecified",
                }
                for x in request.env["res.partner"]
                .sudo()
                .search([("customer_class_id.is_wholesales", "=", True), ("is_company", "=", True)])
                .sorted(lambda m: m.name)
            ],
            "company": [
                {
                    "id": x.id,
                    "name": x.name or "Unspecified",
                }
                for x in request.env["res.company"].sudo().search([]).sorted(lambda m: m.name)
            ],
        }

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

    def _get_sale_orders(
        self,
        start_date,
        end_date,
        salesperson,
        country,
        brand,
        warehouse,
        wholesale_customers,
        company_id=False,
        delivery_status=False,
    ):
        """
        Get sale orders according to the filters
        """
        # Filter data
        filter_where_clause = ""
        # if not company_id:
        #     filter_where_clause += 'AND so.magento_website_id in (1, 2, 3, 13)'
        if salesperson != "all":
            filter_where_clause += f"AND so.user_id = {int(salesperson)} "
        if country != "all":
            filter_where_clause += f"AND irp.country_id = {int(country)} "
        if brand != "all":
            filter_where_clause += f"AND pt.product_breeder_id = {int(brand)} "
        if warehouse != "all":
            filter_where_clause += f"AND so.warehouse_id = {int(warehouse)} "
        if company_id:
            filter_where_clause += f"AND so.company_id = {int(company_id)} "
        if delivery_status:
            filter_where_clause += f"AND so.delivery_status in ('done') "
        if wholesale_customers != "all":
            filter_where_clause += f"AND so.partner_id = {int(wholesale_customers)} "
        filter_where_clause += f"AND so.state in ('sale') "
        select = """
        -- so.id AS so_id,
        sol.id AS sol_id,
        so.name,
        so.user_id,
        so.partner_id,
        so.date_order,
        so.amount_total,
        sol.order_id AS order_id,
        pt.list_price ,
        sol.price_subtotal,
        CASE WHEN pt.breed_available_in_dashboard = TRUE THEN pt.product_breeder_id ELSE null END as product_breeder_id,
        --pt.product_breeder_id,
        sol.product_uom_qty,
        pt.detailed_type,
        sol.product_id as product_id,
        pt.name as product_name,
        pt.default_code
        """
        ObjModuleSudo = request.env["ir.module.module"].sudo()
        margin_enabled = ObjModuleSudo.search(
            [("name", "=", "sale_margin"), ("state", "=", "installed")]
        ) or ObjModuleSudo.search([("name", "=", "sale_margin_extension"), ("state", "=", "installed")])
        if margin_enabled:
            select += ", sol.margin"
        else:
            select += ", 0.00 AS margin"
        query = """
                SELECT {select}
                FROM sale_order so
                LEFT JOIN res_partner irp ON irp.id = so.partner_shipping_id
                LEFT JOIN res_partner rp ON rp.id = so.partner_id
                LEFT JOIN customer_class cc ON cc.id = rp.customer_class_id
                LEFT JOIN sale_order_line sol ON sol.order_id = so.id
                LEFT JOIN product_product pp ON pp.id = sol.product_id
                LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                WHERE so.date_order >= '{start_date}'
                AND so.date_order <= '{end_date}'
                AND cc.is_wholesales IS TRUE
                {filter_where_clause}
                """.format(
            select=select, start_date=start_date, end_date=end_date, filter_where_clause=filter_where_clause
        )
        request.env.cr.execute(query)
        data = request.env.cr.dictfetchall()
        return data

    def _prepare_bar_chart_data(self, start_date, end_date, records):
        """
        Generate bar chart data for given date period and given recordset
        """
        # --------------------
        datasets = []
        dates = self._compute_months_with_years(start_date, end_date)
        data = []
        bg_color = ["rgb(255, 0, 0)"]
        for m_d in dates:
            # Prepare monthly data
            month_start_date = m_d
            month_end_date = m_d + relativedelta(months=+1)
            sol_data = list(
                filter(lambda x: month_start_date <= x["date_order"] <= (month_end_date - timedelta(days=1)), records)
            )
            so_ids = list({x["order_id"] for x in sol_data})
            amount_total, margin, margin_percent = self._compute_sale_order_total(so_ids)
            data.append(amount_total)
            # data.append(sum([x['price_subtotal'] for x in sale_orders]))

        datasets.append(
            {
                "label": "Sale Orders",
                "data": data,
                "backgroundColor": bg_color,
                "borderColor": bg_color,
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

    @http.route("/tgr/dashboard/get_completed_orders_data", type="json", auth="user")
    def get_completed_orders_data(
        self, start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers, *kw
    ):
        """
        Prepare completed orders bar chart data
        """
        start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        data = self._get_sale_orders(start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers)
        data = {
            "labels": self._prepare_labels(start_date, end_date),
            "datasets": self._prepare_bar_chart_data(start_date, end_date, data),
        }
        x_title = "Months"
        return self._prepare_barchart_options(x_title, "Orders", data)

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

    def _prepare_sales_and_profit_area_chart_data(self, start_date, end_date, records):
        """
        Generate bar chart data for given date period and given recordset
        """
        datasets = []
        dates = self._compute_months_with_years(start_date, end_date)
        revenue_data = []
        profit_data = []
        for m_d in dates:
            # Prepare monthly data
            month_start_date = m_d
            month_end_date = m_d + relativedelta(months=+1)
            sol_data = list(
                filter(lambda x: month_start_date <= x["date_order"] <= (month_end_date - timedelta(days=1)), records)
            )
            so_ids = list({x["order_id"] for x in sol_data})
            amount_total, margin, margin_percent = self._compute_sale_order_total(so_ids)
            # revenue_data.append(sum([x['price_subtotal'] for x in sol_data]))
            revenue_data.append(amount_total)
            profit_data.append(
                sum(x["price_subtotal"] for x in sol_data)
                - sum(x["list_price"] for x in sol_data if x["list_price"] not in [False, None])
            )
        datasets.extend(
            [
                {
                    "label": "Profit",
                    "data": profit_data,
                    "borderColor": "rgb(255, 99, 132)",
                    "backgroundColor": "rgb(255, 99, 132, 0.3)",
                    "fill": "start",
                },
                {
                    "label": "Revenue",
                    "data": revenue_data,
                    "borderColor": "rgb(102, 153, 0)",
                    "backgroundColor": "rgb(102, 153, 0, 0.3)",
                    "fill": "start",
                },
            ]
        )
        return datasets

    def _prepare_areachart_options(self, x_title, y_title, data, crm=False):
        """
        Prepare options for areachart
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
                        "position": "right" if crm else "top",
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

    @http.route("/tgr/dashboard/get_sales_and_profit_data", type="json", auth="user")
    def get_sales_and_profit_data(
        self, start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers, *kw
    ):
        """
        Prepare sales and profit area chart data
        """
        start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        sale_orders = self._get_sale_orders(
            start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers
        )
        data = {
            "labels": self._prepare_labels(start_date, end_date),
            "datasets": self._prepare_sales_and_profit_area_chart_data(start_date, end_date, sale_orders),
        }
        x_title = "Month"
        return self._prepare_areachart_options(x_title, "Sales and Profit", data)

    def _prepare_sales_by_brand_pie_chart_data(self, start_date, end_date, records):
        """
        Generate pie chart data for given date period and given recordset
        """
        product_brand_ids = list(
            {x["product_breeder_id"] for x in records if x["product_breeder_id"] not in (None, False)}
        )
        labels = ["Other"] + [request.env["product.breeder"].sudo().browse(x).breeder_name for x in product_brand_ids]
        data = [
            sum(x["product_uom_qty"] for x in filter(lambda x: x["product_breeder_id"] in (False, None), records))
        ]
        pie_chart_color = ["rgb(26, 26, 255)"]
        for brand in product_brand_ids:
            data.append(
                sum(x["product_uom_qty"] for x in list(filter(lambda x: x["product_breeder_id"] == brand, records)))
            )
            pie_chart_color.append(request.env["product.breeder"].sudo().browse(brand).dashboard_rgb_color_code)
        pie_chart_data = {
            "labels": labels,
            "datasets": [{"data": data, "label": "Brands", "backgroundColor": pie_chart_color, "hoverOffset": 4}],
        }
        return pie_chart_data

    def _prepare_piechart_options(self, data):
        """
        Prepare options for pie chart
        """
        return {
            "type": "pie",
            "data": data,
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "position": "right",
                    },
                    "title": {"position": "bottom", "display": True, "fullSize": True},
                },
            },
        }

    @http.route("/tgr/dashboard/get_sales_by_brand_data", type="json", auth="user")
    def get_sales_by_brand_data(
        self, start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers, *kw
    ):
        """
        Prepare sales by brand pie chart data
        """
        start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        sale_orders = self._get_sale_orders(
            start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers
        )
        data = self._prepare_sales_by_brand_pie_chart_data(start_date, end_date, sale_orders)
        return self._prepare_piechart_options(data)

    def _prepare_margin_area_chart_data(self, start_date, end_date, records):
        """
        Generate area chart data for given date period and given recordset
        """
        datasets = []
        dates = self._compute_months_with_years(start_date, end_date)
        margin_data = []
        for m_d in dates:
            # Prepare monthly data
            month_start_date = m_d
            month_end_date = m_d + relativedelta(months=+1)
            sol_data = list(
                filter(lambda x: month_start_date <= x["date_order"] <= (month_end_date - timedelta(days=1)), records)
            )
            so_ids = list({x["order_id"] for x in sol_data})
            amount_total, margin, margin_percent = self._compute_sale_order_total(so_ids)
            # margin = sum([x['margin'] for x in sale_orders])
            # amount_total = sum([x['price_subtotal'] for x in sale_orders])
            # margin = (margin / amount_total * 100) if amount_total != 0 else 0.00
            margin = margin_percent and margin_percent or 0.00
            margin_data.append(margin)
        datasets.extend(
            [
                {
                    "label": "Margin",
                    "data": margin_data,
                    "borderColor": "rgb(255, 170, 128)",
                    "backgroundColor": "rgb(255, 170, 128, 0.3)",
                    "fill": "start",
                }
            ]
        )
        return datasets

    @http.route("/tgr/dashboard/get_margin_data", type="json", auth="user")
    def get_margin_data(self, start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers, *kw):
        """
        Prepare margin area chart data
        """
        start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        sale_orders = self._get_sale_orders(
            start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers
        )
        data = {
            "labels": self._prepare_labels(start_date, end_date),
            "datasets": self._prepare_margin_area_chart_data(start_date, end_date, sale_orders),
        }
        x_title = "Month"
        return self._prepare_areachart_options(x_title, "Margin", data)

    def _prepare_phyto_nation_chart_data(self, start_date, end_date, records):
        """
        Generate area chart data for given date period and given recordset
        """
        datasets = []
        dates = self._compute_months_with_years(start_date, end_date)
        # partner_ids = records.sudo().mapped('partner_id')
        partner_ids = list({x["partner_id"] for x in records})
        for partner_id in partner_ids:
            # data = [sum([so['price_subtotal'] for so in list(filter(lambda y: (x <= y['date_order'] <= (x + relativedelta(months=+1) - timedelta(days=1))) and y['partner_id'] == partner_id, records))]) for x in dates]
            data = []
            for d in dates:
                sol_data = list(
                    filter(
                        lambda y: (d <= y["date_order"] <= (d + relativedelta(months=+1) - timedelta(days=1)))
                        and y["partner_id"] == partner_id,
                        records,
                    )
                )
                so_ids = list({x["order_id"] for x in sol_data})
                so_total, margin, margin_percent = self._compute_sale_order_total(so_ids)
                data.append(so_total)
            partner_id = request.env["res.partner"].sudo().browse(partner_id)
            datasets.extend(
                [
                    {
                        "label": partner_id.name,
                        "data": data,
                        "borderColor": partner_id.phytonation_chart_color_code,
                        # 'backgroundColor': 'rgb(255, 170, 128, 0.3)',
                        "fill": False,
                    }
                ]
            )
        return datasets

    @http.route("/tgr/dashboard/get_phyto_nation_area_chart", type="json", auth="user")
    def get_phyto_nation_area_chart(
        self, start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers, *kw
    ):
        """
        Prepare phytonation area chart data
        """
        start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        sale_orders = self._get_sale_orders(
            start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers, company_id=9
        )  # TODO Enable when adding to production
        # sale_orders = self._get_sale_orders(start_date, end_date, salesperson, country, brand, warehouse)
        data = {
            "labels": self._prepare_labels(start_date, end_date),
            "datasets": self._prepare_phyto_nation_chart_data(start_date, end_date, sale_orders),
        }
        x_title = "Month"
        return self._prepare_areachart_options(x_title, "Phytonation Sales", data)

    @http.route("/tgr/dashboard/get_summary_data", type="json", auth="user")
    def get_summary_data(self, start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers, *kw):
        """
        Prepare summary data
        """
        start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        sale_orders = self._get_sale_orders(
            start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers
        )
        sale_ids = list({x["order_id"] for x in sale_orders})
        total_orders = f"{len(sale_ids)}"
        # amount_total = sum(x['price_subtotal'] for x in sale_orders)
        amount_total, margin, margin_percent = self._compute_sale_order_total(sale_ids)
        amount_cost = sum(x["list_price"] for x in sale_orders if x["list_price"] not in [None, False])
        total_revenue = "{:.2f}".format(amount_total)
        total_revenue = f"€ {total_revenue}"
        total_profit = "{:.2f}".format(amount_total - amount_cost)
        total_profit = f"€ {total_profit}"
        total_margin = "{:.2f}".format(sum(x["margin"] and x["margin"] or False for x in sale_orders))
        return {"orders": total_orders, "revenue": total_revenue, "profit": total_profit, "margin": total_margin, 'margin_percent': margin_percent and str(round(margin_percent, 3)) + ' %' or "0.00 %"}

    def _compute_sale_order_total(self, so_ids):
        """
        @private: get sale order total for given sale order ids
        """
        if so_ids:
            select = """ SUM(amount_total) AS so_amount"""
            if (
                request.env["ir.module.module"]
                .sudo()
                .search([("name", "=", "sale_margin"), ("state", "=", "installed")])
            ):
                select += ", SUM(margin) AS margin, SUM(margin_percent) as margin_percent"
            else:
                select += ", 0.00 AS margin, 0.00 AS margin_percent"
            if len(so_ids) == 1:
                where_clause = """ WHERE id = {sale_ids}""".format(sale_ids=so_ids[0])
            else:
                where_clause = """ WHERE id in {sale_ids}""".format(sale_ids=tuple(so_ids))
            query = """
            SELECT {select}
            FROM sale_order
            {where_clause}
            """.format(
                select=select, where_clause=where_clause
            )
            request.env.cr.execute(query)
            data = request.env.cr.dictfetchall()
            so_amount, margin, margin_percent = 0, 0, 0
            if data:
                so_amount, margin, margin_percent = data[0]["so_amount"], data[0]["margin"], data[0]["margin_percent"]
        else:
            so_amount, margin, margin_percent = 0, 0, 0
        return so_amount, margin, margin_percent

    @http.route("/tgr/dashboard/prepare_amount_of_each_product_sale", type="json", auth="user")
    def prepare_amount_of_each_product_sale(
        self, start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers, sort, *kw
    ):
        """
        Prepare data for amount of each product sale
        """
        start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        sale_orders = self._get_sale_orders(
            start_date, end_date, salesperson, country, brand, warehouse, wholesale_customers
        )
        data = {"lines": [], "total": ""}
        if brand != "all":
            product_ids = list(
                {
                        (x["product_id"], x["product_name"], x["default_code"])
                        for x in sale_orders
                        if (x["detailed_type"] == "product") and (x["product_breeder_id"] == int(brand))
                }
            )
        else:
            product_ids = list(
                {
                        (x["product_id"], x["product_name"], x["default_code"])
                        for x in sale_orders
                        if x["detailed_type"] == "product"
                }
            )

        for product in product_ids:
            product_uom_qty = sum(x["product_uom_qty"] for x in sale_orders if x["product_id"] == product[0])
            data["lines"].append(
                {
                    "item_description": product[1],
                    "inventory_id": product[2],
                    "sales_qty": product_uom_qty,
                    "sales_qty_str": "{:.2f}".format(product_uom_qty),
                }
            )
        data["total"] = "{:.2f}".format(sum(x["product_uom_qty"] for x in sale_orders))
        # sort values
        sort_type = sort.split("-")[1]
        reverse = True if sort_type == "dsc" else False
        data["lines"].sort(key=lambda x: x[sort.split("-")[0]], reverse=reverse)
        return data

    # =================================================================================================
    # CRM Dashboard
    # =================================================================================================

    def _get_leads(self, start_date, end_date, salesperson, country):
        """
        @private - Get leads for the filters
        """
        domain = [("create_date", ">=", start_date), ("create_date", "<=", end_date)]
        if salesperson != "all":
            domain.append(("user_id", "=", int(salesperson)))
        # if country != 'all':
        #     domain.append(('country_id', '=', int(country)))
        return request.env["crm.lead"].sudo().search(domain)

    def _prepare_salesperson_vs_revenue_data(self, salesperson, lead_ids):
        """
        @private - Get data for the salesperson vs revenue data chart
        """
        if salesperson != "all":
            salesperson_ids = request.env["res.users"].sudo().browse(int(salesperson))
        else:
            salesperson_ids = request.env["res.users"].sudo().search([])
        datasets = []

        def _get_lead_data(crm_lead_ids):
            """
            @private: get necessary lead data
            """
            won_stage_id = request.env["crm.stage"].sudo().search([("is_won", "=", True)], limit=1)
            new_stage_id = request.env["crm.stage"].sudo().search([("id", "=", 1)], limit=1)
            new_leads = crm_lead_ids.filtered(lambda x: x.stage_id.id == new_stage_id.id)
            # leads_converted = crm_lead_ids.filtered(lambda x: x.stage_id.id == won_stage_id.id)
            leads_converted_purchase = crm_lead_ids.filtered(lambda x: x.quotation_count > 0 or x.sale_order_count > 0)
            total_rev_from_converted_leads = sum(leads_converted_purchase.mapped("sale_amount_total"))
            total_rev_from_new_customers = sum(new_leads.mapped("expected_revenue"))
            return [len(leads_converted_purchase), total_rev_from_converted_leads, total_rev_from_new_customers]

        for salesperson_id in salesperson_ids:
            leads = lead_ids.filtered(lambda x: x.user_id.id == salesperson_id.id)
            datasets.extend(
                [
                    {
                        "label": salesperson_id.name,
                        "data": _get_lead_data(leads),
                        "borderColor": salesperson_id.dashboard_chart_rgb_color,
                        # 'backgroundColor': 'rgb(255, 170, 128, 0.3)',
                        "fill": False,
                    }
                ]
            )
        leads_without_users = lead_ids.filtered(lambda l: not l.user_id)
        if leads_without_users:
            datasets.extend(
                [
                    {
                        "label": "Unassigned",
                        "data": _get_lead_data(leads_without_users),
                        "borderColor": "rgb(255, 170, 128)",
                        # 'backgroundColor': 'rgb(255, 170, 128, 0.3)',
                        "fill": False,
                    }
                ]
            )
        return {
            "labels": [
                ["Number of leads", " now purchasing", " customers"],
                ["Total Revenue", " from all Purchasing", " Customers"],
                ["Total Revenue", "From Newly", " Converted Customers"],
            ],
            "datasets": datasets,
        }

    @http.route("/tgr/dashboard/get_salesperson_vs_revenue_data", type="json", auth="user")
    def get_salesperson_vs_revenue_data(self, start_date, end_date, salesperson, country, *kw):
        """
        Prepare salesperson vs revenue data
        """
        start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        leads = self._get_leads(start_date, end_date, salesperson, country)
        data = self._prepare_salesperson_vs_revenue_data(salesperson, leads)
        x_title = ""
        return self._prepare_areachart_options(x_title, "Numbers", data, crm=False)

    @http.route("/tgr/dashboard/prepare_leads_information", type="json", auth="user")
    def prepare_leads_information(self, start_date, end_date, salesperson, country, *kw):
        """
        Prepare data for amount of each product sale
        """
        start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        leads = self._get_leads(start_date, end_date, salesperson, country)
        data = {"lines": []}
        for customer_id in leads.mapped("partner_id"):
            data["lines"].append(
                {
                    "customer_name": customer_id.name,
                    "country_id": customer_id.country_id.code or "",
                }
            )
        return data

    @http.route("/tgr/dashboard/prepare_leads_and_conversions", type="json", auth="user")
    def prepare_leads_and_conversions(self, start_date, end_date, salesperson, country, *kw):
        """
        Prepare data for leads and conversions
        """
        start_date, end_date = self._compute_start_end_dates(start_date, end_date)
        leads = self._get_leads(start_date, end_date, salesperson, country)
        won_stage_id = request.env["crm.stage"].sudo().search([("is_won", "=", True)], limit=1)
        new_stage_id = request.env["crm.stage"].sudo().search([("id", "=", 1)], limit=1)
        data = {"lines": []}
        for user_id in leads.mapped("user_id"):
            lead_ids = leads.filtered(lambda x: x.user_id.id == user_id.id)
            new_leads = lead_ids.filtered(lambda x: x.stage_id.id == new_stage_id.id)
            leads_converted = lead_ids.filtered(lambda x: x.stage_id.id == won_stage_id.id)
            leads_converted_purchase = lead_ids.filtered(lambda x: x.quotation_count > 0 or x.sale_order_count > 0)
            total_rev_from_converted_leads = sum(leads_converted_purchase.mapped("sale_amount_total"))
            total_rev_from_new_customers = sum(new_leads.mapped("expected_revenue"))
            leads_to_purchase_conversion_rate = (
                ((len(leads_converted_purchase) / len(leads_converted)) * 100) if len(leads_converted) > 0 else 0.00
            )
            data["lines"].append(
                {
                    "salesperson": user_id.name,
                    "number_of_leads": len(lead_ids),
                    "new_leads": len(new_leads),
                    "leads_converted_c": len(leads_converted),
                    "leads_converted_pc": len(leads_converted_purchase),
                    "total_revenue_from_converted_leads": f"€ {total_rev_from_converted_leads}",
                    "total_revenue_from_new_customers": f"€ {total_rev_from_new_customers}",
                    "leads_to_purchase_conversion_rate": f"{leads_to_purchase_conversion_rate} %",
                }
            )
        return data
