odoo.define('tgr_dashboards.sales_dashboard', function (require) {
    "use strict";

    let AbstractAction = require('web.AbstractAction');
    let core = require('web.core');

    let tgrSalesDashboard = AbstractAction.extend({
        contentTemplate: 'tgrSalesDashboard',

        cssLibs: [
            '/tgr_dashboards/static/src/css/libs/daterangepicker.css',
        ],

        jsLibs: [
            '/tgr_dashboards/static/src/js/libs/daterangepicker.min.js',
            '/tgr_dashboards/static/src/js/libs/moment.min.js',
            '/tgr_dashboards/static/src/js/libs/chart.min.js',
            '/tgr_dashboards/static/src/js/libs/chartjs-plugin-datalabels.min.js',
        ],

        events: {
            'change #country': '_onchangeCountry',
            'change #brand': '_onchangeBrand',
            'change #salesperson': '_onchangeSalesPerson',
            'change #warehouse': '_onchangeWarehouse',
            'change #wholesale_customers': '_onchangeWholesale_customers',
            'change #sort-field': '_onchangeSortAmountEachProductSold',
            'click .redirect-to-sale-orders': '_redirectToSaleOrders'
        },

        /**
         * @private
         * Redirect to assigned sale orders
         */
        _redirectToSaleOrders: function () {
            let self = this;
            this._rpc({
                route: '/tgr/dashboard/get_summary_sale_view_action',
                params: {
                    start_date: this.startDate,
                    end_date: this.endDate,
                    salesperson: $('#salesperson').val(),
                    country: $('#country').val(),
                    brand: $('#brand').val(),
                    warehouse: $('#warehouse').val(),
                    wholesale_customers: $('#wholesale_customers').val(),
                },
            }).then(function (action) {
                self.do_action(action, {clear_breadcrumbs: true});
                // self.do_action(action);
            })
        },

        /**
         * @private
         * Change data when changing sorting
         */
        _onchangeSortAmountEachProductSold: function () {
            this._updateChartData()
        },

        /**
         * @private
         * Change data when changing country field
         */
        _onchangeCountry: function () {
            this._updateChartData()
        },

        /**
         * @private
         * Change data when changing brand field
         */
        _onchangeBrand: function () {
            this._updateChartData()
        },

        /**
         * @private
         * Change data when changing salesperson field
         */
        _onchangeSalesPerson: function () {
            this._updateChartData()
        },

        /**
         * @private
         * Change data when changing warehouse field
         */
        _onchangeWarehouse: function () {
            this._updateChartData()
        },

        /**
         * @private
         * Change data when changing warehouse field
         */
        _onchangeWholesale_customers: function () {
            this._updateChartData()
        },


        /**
         * @private
         * Function for update data in charts
         */
        _updateChartData: function () {
            let params = {
                start_date: this.startDate,
                end_date: this.endDate,
                salesperson: $('#salesperson').val(),
                country: $('#country').val(),
                brand: $('#brand').val(),
                warehouse: $('#warehouse').val(),
                wholesale_customers: $('#wholesale_customers').val(),
            }
            if (!this.dateInitialized) {
                // Update completed orders bar chart data
                let completedOrders = Chart.getChart("completedOrders")
                this._rpc({
                    route: '/tgr/dashboard/get_completed_orders_data',
                    params: params,
                }).then(function (data) {
                    completedOrders.data.labels = data.data.labels;
                    completedOrders.data.datasets = data.data.datasets;
                    completedOrders.update();
                });
                // Update sales and profit area chart data
                let salesAndProfit = Chart.getChart("salesAndProfit")
                this._rpc({
                    route: '/tgr/dashboard/get_sales_and_profit_data',
                    params: params,
                }).then(function (data) {
                    salesAndProfit.data.labels = data.data.labels;
                    salesAndProfit.data.datasets = data.data.datasets;
                    salesAndProfit.update();
                });
                // Update sales by brand pie chart data
                let salesByBrand = Chart.getChart("salesByBrand")
                this._rpc({
                    route: '/tgr/dashboard/get_sales_by_brand_data',
                    params: params,
                }).then(function (data) {
                    salesByBrand.data.labels = data.data.labels;
                    salesByBrand.data.datasets = data.data.datasets;
                    salesByBrand.update();
                });
                // Update margin area chart data
                let marginAreaChart = Chart.getChart("marginAreaChart")
                this._rpc({
                    route: '/tgr/dashboard/get_margin_data',
                    params: params,
                }).then(function (data) {
                    marginAreaChart.data.labels = data.data.labels;
                    marginAreaChart.data.datasets = data.data.datasets;
                    marginAreaChart.update();
                });
                // Update phytonation sales area chart data
                let phytoNationSalesAreaChart = Chart.getChart("phytoNationSalesAreaChart")
                this._rpc({
                    route: '/tgr/dashboard/get_phyto_nation_area_chart',
                    params: params,
                }).then(function (data) {
                    phytoNationSalesAreaChart.data.labels = data.data.labels;
                    phytoNationSalesAreaChart.data.datasets = data.data.datasets;
                    phytoNationSalesAreaChart.update();
                });
                // update summary data values
                this._prepareSummaryData();
                // update table prepare amount of each product sale
                this._prepareAmountOfEachProductSale();
            }
        },

        /**
         * @private
         * Prepare filter values
         */
        _prepareFilterValues: function () {
            this._rpc({
                route: '/tgr/dashboard/get_filter_values',
            }).then(function (data) {
                // Countries
                data.countries.forEach(function (country) {
                    $('#country').append($('<option>', {
                        value: country.id,
                        text : country.name
                    }));
                });
                // Salespersons
                data.salespersons.forEach(function (salesperson) {
                    $('#salesperson').append($('<option>', {
                        value: salesperson.id,
                        text : salesperson.name
                    }));
                });
                // Brands
                data.brands.forEach(function (brand) {
                    $('#brand').append($('<option>', {
                        value: brand.id,
                        text : brand.name
                    }));
                })
                // Warehouses
                data.warehouses.forEach(function (warehouse) {
                    $('#warehouse').append($('<option>', {
                        value: warehouse.id,
                        text : warehouse.name
                    }));
                })
                //Wholesale Customer
                data.wholesale_customers.forEach(function (wholesale_customers) {
                    $('#wholesale_customers').append($('<option>', {
                        value: wholesale_customers.id,
                        text : wholesale_customers.name
                    }));
                })
            });
        },

        /**
         * @private
         * Prepare summary data
         */
        _prepareSummaryData: function () {
            let params = {
                start_date: this.startDate,
                end_date: this.endDate,
                salesperson: $('#salesperson').val(),
                country: $('#country').val(),
                brand: $('#brand').val(),
                warehouse: $('#warehouse').val(),
                wholesale_customers: $('#wholesale_customers').val(),
            }
            this._rpc({
                route: '/tgr/dashboard/get_summary_data',
                params: params,
            }).then(function (data) {
                $('.total-orders').text(data.orders);
                $('.total-revenue').text(data.revenue);
                $('.total-profit').text(data.profit);
                $('.total-margin').text(data.margin);
                $('.total-margin_percent').text(data.margin_percent);
            })
        },

        /**
         * @private
         * Prepare amount of each product sale data
         */
        _prepareAmountOfEachProductSale: function () {
            let params = {
                start_date: this.startDate,
                end_date: this.endDate,
                salesperson: $('#salesperson').val(),
                country: $('#country').val(),
                brand: $('#brand').val(),
                warehouse: $('#warehouse').val(),
                wholesale_customers: $('#wholesale_customers').val(),
                sort: $('#sort-field').val()
            }
            this._rpc({
                route: '/tgr/dashboard/prepare_amount_of_each_product_sale',
                params: params,
            }).then(function (data) {
                let tableBodyText = '';
                data.lines.forEach(function(line) {
                    tableBodyText += '<tr><td class="text-left">' + line.item_description + '</td><td class="text-left">' + line.inventory_id + '</td><td class="text-right">' + line.sales_qty_str + '</td></tr>'
                });
                tableBodyText += '<tr><th class="text-left" colspan="2">Total</th><th class="text-right">' + data.total + '</th></tr>'
                $('.amount-of-each-product-sold-tbody').html(tableBodyText);
            })
        },

        /**
         * @override
         * Initialize necessary variables
         */
        init: function (parent, params) {
            this._super.apply(this, arguments);
            this.startDate = moment().startOf('month');
            this.endDate = moment().endOf('month');
            this.dateInitialized = true;
            // Register chart datalables
            // Chart.register(ChartDataLabels);
        },

        /**
         * @private
         * Update chart data when onchange date
         */
        _onchangeDate: function (start_date, end_date) {
            this.startDate = start_date;
            this.endDate = end_date;
            this._updateChartData();
            this.dateInitialized = false;
        },

        /**
         * @private
         * Prepare date range for date filters
         */
        _prepareDateRange: function () {
            let start = moment().startOf('month');
            let end = moment().endOf('month');
            let self = this;
            function cb(start, end) {
                $('#chart-date-range #load-data').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
                self._onchangeDate(start, end)
            }
            $('#chart-date-range').daterangepicker({
                startDate: start,
                endDate: end,
                opens: 'left',
                ranges: {
                    'This Month': [moment().startOf('month'), moment().endOf('month')],
                    'Last 30 Days': [moment().subtract(29, 'days'), moment()],
                    'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
                    'This Year': [moment().startOf('year'), moment()]
                }
            }, cb);
            cb(start, end)
        },

        /**
         * @private
         * Increase the spacing between legend and Chart
         */
        _increaseSpacingBetweenLegendAndChart: function () {
            return [{
                beforeInit : function (chart) {
                    // Get reference to the original fit function
                    const originalFit = chart.legend.fit;

                    // Override the fit function
                    chart.legend.fit = function fit() {
                        // Call original function and bind scope in order to use `this` correctly inside it
                        originalFit.bind(chart.legend)();
                        // Change the height as suggested in another answers
                        this.height += 20;
                    }
                }
            }]
        },

        /**
         * @private
         * Prepare completed orders bar chart with data
         */
        _prepareCompletedOrdersBarChart: function () {
            let self = this;
            this._rpc({
                route: '/tgr/dashboard/get_completed_orders_data',
                params: {
                    start_date: this.startDate,
                    end_date: this.endDate,
                    salesperson: $('#salesperson').val(),
                    country: $('#country').val(),
                    brand: $('#brand').val(),
                    warehouse: $('#warehouse').val(),
                    wholesale_customers: $('#wholesale_customers').val(),
                },
            }).then(function (data) {
                // Increase spacing between legend and chart
                data.plugins = self._increaseSpacingBetweenLegendAndChart()
                // Render bar chart
                let completedOrdersBarChart = new Chart($('#completedOrders'), data);
                completedOrdersBarChart.render()
            });
        },

        /**
         * @private
         * Prepare sales and profit area chart with data
         */
        _prepareSalesAndProfitAreaChart: function () {
            let self = this;
            this._rpc({
                route: '/tgr/dashboard/get_sales_and_profit_data',
                params: {
                    start_date: this.startDate,
                    end_date: this.endDate,
                    salesperson: $('#salesperson').val(),
                    country: $('#country').val(),
                    brand: $('#brand').val(),
                    warehouse: $('#warehouse').val(),
                    wholesale_customers: $('#wholesale_customers').val(),
                },
            }).then(function (data) {
                // Increase spacing between legend and chart
                data.plugins = self._increaseSpacingBetweenLegendAndChart()
                // Render area chart
                let salesAndProfitAreaChart = new Chart($('#salesAndProfit'), data);
                salesAndProfitAreaChart.render()
            });
        },

        /**
         * @private
         * Prepare sales by brand pie chart with data
         */
        _prepareSalesByBrandPieChart: function () {
            let self = this;
            this._rpc({
                route: '/tgr/dashboard/get_sales_by_brand_data',
                params: {
                    start_date: this.startDate,
                    end_date: this.endDate,
                    salesperson: $('#salesperson').val(),
                    country: $('#country').val(),
                    brand: $('#brand').val(),
                    warehouse: $('#warehouse').val(),
                    wholesale_customers: $('#wholesale_customers').val(),
                },
            }).then(function (data) {
                // Render pie chart
                let salesByBrandPieChart = new Chart($('#salesByBrand'), data);
                salesByBrandPieChart.render()
            });
        },

        /**
         * @private
         * Prepare margin area chart with data
         */
        _prepareMarginAreaChart: function () {
            let self = this;
            this._rpc({
                route: '/tgr/dashboard/get_margin_data',
                params: {
                    start_date: this.startDate,
                    end_date: this.endDate,
                    salesperson: $('#salesperson').val(),
                    country: $('#country').val(),
                    brand: $('#brand').val(),
                    warehouse: $('#warehouse').val(),
                    wholesale_customers: $('#wholesale_customers').val(),
                },
            }).then(function (data) {
                // Increase spacing between legend and chart
                data.plugins = self._increaseSpacingBetweenLegendAndChart()
                // Render pie chart
                let marginAreaChart = new Chart($('#marginAreaChart'), data);
                marginAreaChart.render()
            });
        },

        /**
         * @private
         * Prepare phyto nation area chart with data
         */
        _prepareaPhytoNationSalesAreaChart: function () {
            let self = this;
            this._rpc({
                route: '/tgr/dashboard/get_phyto_nation_area_chart',
                params: {
                    start_date: this.startDate,
                    end_date: this.endDate,
                    salesperson: $('#salesperson').val(),
                    country: $('#country').val(),
                    brand: $('#brand').val(),
                    warehouse: $('#warehouse').val(),
                    wholesale_customers: $('#wholesale_customers').val(),
                },
            }).then(function (data) {
                // Increase spacing between legend and chart
                data.plugins = self._increaseSpacingBetweenLegendAndChart()
                // Render pie chart
                let phytoNationAreaChart = new Chart($('#phytoNationSalesAreaChart'), data);
                phytoNationAreaChart.render()
            });
        },

        /**
         * @override
         * Initialize charts, filters
         */
        on_attach_callback: function () {
            this._super();
            this._prepareCompletedOrdersBarChart();
            this._prepareSalesAndProfitAreaChart();
            this._prepareSalesByBrandPieChart();
            this._prepareMarginAreaChart();
            this._prepareDateRange();
            this._prepareFilterValues();
            this._prepareSummaryData();
            this._prepareAmountOfEachProductSale();
            this._prepareaPhytoNationSalesAreaChart();
        },

    });

    // load client action
    core.action_registry.add('tgr_sales_dashboard', tgrSalesDashboard);

    return {
        MainMenu: tgrSalesDashboard,
    };

});
