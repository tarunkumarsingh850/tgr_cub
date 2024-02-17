odoo.define('tgr_dashboards.purchase_dashboard', function (require) {
    "use strict";

    let AbstractAction = require('web.AbstractAction');
    let core = require('web.core');
    let datas = {}

    let tgrPurchaseDashboard = AbstractAction.extend({
        contentTemplate: 'tgrPurchaseDashboard',

        cssLibs: [
            '/tgr_dashboards/static/src/css/libs/daterangepicker.css',
            '/tgr_dashboards/static/src/css/libs/jquery.multiselect.css',
        ],

        jsLibs: [
            '/tgr_dashboards/static/src/js/libs/jquery.multiselect.js',
            '/tgr_dashboards/static/src/js/libs/daterangepicker.min.js',
            '/tgr_dashboards/static/src/js/libs/moment.min.js',
            '/tgr_dashboards/static/src/js/libs/chart.min.js',
            '/tgr_dashboards/static/src/js/libs/chartjs-plugin-datalabels.min.js',
        ],

        events: {
            'change #country': '_onchangeCountry',
            'change #brand': '_onchangeBrand',
            'change #warehouse': '_onchangeWarehouse',
            'change .sob-filters': '_onchangeSOBFilters',
            'change #paginationPage': '_onchangePagination',
            'keypress #paginationPage': '_onKeypress',
            'change #paginationPageCSL': '_onchangePaginationCSL',
            'keypress #paginationPageCSL': '_onKeypressCSL',
            'click .print_sales_of_brand' : 'action_print_xls'
        },

        action_print_xls: function(ev){
            ev.preventDefault()
            var self = this;
            this._rpc({
                model: 'sob.print.success.box',
                method: 'print_sob_xls_report',
                args: [3,datas],
            }).then(function(result){
                self.do_action(result)
            })
            },

        _onKeypressCSL: function (ev) {
            if (ev.charCode === $.ui.keyCode.ENTER) {
                this._onchangePaginationCSL(ev)
            }
        },

        _onchangePaginationCSL: function (ev) {
            // update table current stock levels
            this._prepareCurrentStockLevels();
        },

        _onKeypress: function (ev) {
            if (ev.charCode === $.ui.keyCode.ENTER) {
                this._onchangePagination(ev)
            }
        },

        _onchangePagination: function (ev) {
            // Update sales of brand table
            this._prepareSalesOfBrandTable();
        },

        _onchangeSOBFilters: function () {
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
         * Change data when changing warehouse field
         */
        _onchangeWarehouse: function () {
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
                country: $('#country').val(),
                brand: $('#brand').val(),
                warehouse: $('#warehouse').val(),
            }
            if (!this.dateInitialized && !this.dateInitializedSOB) {
                // Update purchase and cogs chart data
                let purchaseCogsLineChart = Chart.getChart("purchaseCogsLineChart")
                this._rpc({
                    route: '/tgr/dashboard/get_purchase_and_cogs_data',
                    params: params,
                }).then(function (data) {
                    purchaseCogsLineChart.data.labels = data.data.labels;
                    purchaseCogsLineChart.data.datasets = data.data.datasets;
                    purchaseCogsLineChart.update();
                });
                // Update purchase and cogs chart data
                let PurchaseStockValueBarChart = Chart.getChart("purchaseStockValuesBarChart")
                this._rpc({
                    route: '/tgr/dashboard/get_stock_value_barchart_data',
                    params: params,
                }).then(function (data) {
                    PurchaseStockValueBarChart.data.labels = data.data.labels;
                    PurchaseStockValueBarChart.data.datasets = data.data.datasets;
                    PurchaseStockValueBarChart.update();
                });
                // update table current stock levels
                this._prepareCurrentStockLevels();
                // Update sell through rate chart data
                let sellThroughRateLineChart = Chart.getChart("sellThroughRateLineChart")
                this._rpc({
                    route: '/tgr/dashboard/get_sell_though_rate_line_chart_data',
                    params: params,
                }).then(function (data) {
                    sellThroughRateLineChart.data.labels = data.data.labels;
                    sellThroughRateLineChart.data.datasets = data.data.datasets;
                    sellThroughRateLineChart.update();
                });
                // Update seedman sales by product bar chart data
                let seedsmanSalesByProductBarChart = Chart.getChart("seedsmanSalesByProductBarChart")
                this._rpc({
                    route: '/tgr/dashboard/get_seedsman_sales_by_product_barchart_data',
                    params: params,
                }).then(function (data) {
                    seedsmanSalesByProductBarChart.data.labels = data.data.labels;
                    seedsmanSalesByProductBarChart.data.datasets = data.data.datasets;
                    seedsmanSalesByProductBarChart.update();
                });
                // update table current stock levels
                this._prepareCurrentStockLevels();
                // Update sales of brand table
                this._prepareSalesOfBrandTable();
            }
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
         * Prepare current stock levels table
         */
        _prepareCurrentStockLevels: function () {
            let params = {
                start_date: this.startDate,
                end_date: this.endDate,
                country: $('#country').val(),
                brand: $('#brand').val(),
                warehouse: $('#warehouse').val(),
                pagination_end: $('#paginationPageCSL').val()
            }
            this._rpc({
                route: '/tgr/dashboard/prepare_current_stock_levels',
                params: params,
            }).then(function (data) {
                $('#paginationPageCSL').val(data.pg_end)
                $('#endPageCSL').text('/    ' + data.all_recs)
                let tableBodyText = '';
                data.lines.forEach(function(line) {
                    tableBodyText += '<tr><td class="text-left">' + line.brand_name + '</td><td class="text-right">' + line.stock_available + '</td><td class="text-right">' + line.stock_value + '</td><td class="text-right">' + line.ideal_stock + '</td><td class="text-right">' + line.stock_value_over_ideal + '</td></tr>'
                });
                tableBodyText += '<tr><th class="text-left">Total</th>' + '<th class="text-right">' + data.total.stock_available_total + '</th>' + '<th class="text-right">' + data.total.stock_value_total + '</th>' + '<th class="text-right">' + data.total.ideal_stock_total + '<th class="text-right">' + data.total.stock_value_over_ideal_total + '</th>' + '</tr>'
                $('.overview-of-current-stock-levels-tbody').html(tableBodyText);
            })
        },

        /**
         * @private
         * Prepare purchase cogs line chart with data
         */
        _preparePurchaseCogsLineChart: function () {
            let self = this;
            this._rpc({
                route: '/tgr/dashboard/get_purchase_and_cogs_data',
                params: {
                    start_date: this.startDate,
                    end_date: this.endDate,
                    country: $('#country').val(),
                    brand: $('#brand').val(),
                    warehouse: $('#warehouse').val(),
                },
            }).then(function (data) {
                // Increase spacing between legend and chart
                data.plugins = self._increaseSpacingBetweenLegendAndChart()
                // Render area chart
                let purchaseCogsLineChart = new Chart($('#purchaseCogsLineChart'), data);
                purchaseCogsLineChart.render()
            });
        },

        /**
         * @private
         * Prepare purchase stock values bar chart with data
         */
        _preparePurchaseStockValueBarChart: function () {
            let self = this;
            this._rpc({
                route: '/tgr/dashboard/get_stock_value_barchart_data',
                params: {
                    start_date: this.startDate,
                    end_date: this.endDate,
                    country: $('#country').val(),
                    brand: $('#brand').val(),
                    warehouse: $('#warehouse').val(),
                },
            }).then(function (data) {
                // Increase spacing between legend and chart
                data.plugins = self._increaseSpacingBetweenLegendAndChart()
                // Render area chart
                let purchaseStockValueBarChart = new Chart($('#purchaseStockValuesBarChart'), data);
                purchaseStockValueBarChart.render()
            });
        },

        /**
         * @private
         * Prepare sell through rate line chart with data
         */
        _prepareSellThroughRateLineChart: function () {
            let self = this;
            this._rpc({
                route: '/tgr/dashboard/get_sell_though_rate_line_chart_data',
                params: {
                    start_date: this.startDate,
                    end_date: this.endDate,
                    country: $('#country').val(),
                    brand: $('#brand').val(),
                    warehouse: $('#warehouse').val(),
                },
            }).then(function (data) {
                // Increase spacing between legend and chart
                data.plugins = self._increaseSpacingBetweenLegendAndChart()
                // Render area chart
                let sellThroughRateLineChart = new Chart($('#sellThroughRateLineChart'), data);
                sellThroughRateLineChart.render()
            });
        },

        /**
         * @private
         * Prepare current stock levels table
         */
        _prepareSalesOfBrandTable: function () {
            let params = {
                start_date: this.startDate,
                end_date: this.endDate,
                country: $('#country').val(),
                brand: $('#brand').val(),
                warehouse: $('#warehouse').val(),
                sob_data: {
                    sob_create_date_start: this.startDateSOB,
                    sob_create_date_end: this.endDateSOB,
                    sob_brand: $('#sob-brand').val(),
                    sob_abc_clarification: $('#sob-abc-classification').val(),
                    sob_sex: $('#sob-sex').val(),
                    sob_flowering_type: $('#sob-flowering-type').val(),
                    sob_odoo_product_tag: $('#sob-odoo-product-tag').val(),
                    sob_product_category: $('#sob-product-group-category').val(),
                    sob_product_segment: $('#sob-product-segment').val(),
                    sob_warehouse: $('#sob-warehouse').val(),
                    sob_website: $('#sob-website').val(),
                    sob_region: $('#sob-region').val(),
                    sob_country: $('#sob-country').val(),
                    sob_company: $('#sob-company').val(),
                    pagination_end: $('#paginationPage').val()
                }
            }
            this._rpc({
                route: '/tgr/dashboard/prepare_sales_of_brand_data',
                params: params,
            }).then(function (data) {
                datas = data
                $('#paginationPage').val(data.pg_end)
                $('#endPage').text('/    ' + data.all_recs)
                let tableBodyText = '';
                data.lines.forEach(function(line) {
                    tableBodyText += '<tr>' +
                        '<td class="text-left">' + line.sku + '</td>' +
                        '<td class="text-left">' + line.brand_name + '</td>' +
                        '<td class="text-left">' + line.name + '</td>' +
                        '<td class="text-right">' + line.inventory_value + '</td>' +
                        '<td class="text-right">' + line.ideal_inventory_value + '</td>' +
                        '<td class="text-right">' + line.inv_value_v_ideal_value + '</td>' +
                        '<td class="text-right">' + line.total_purchases + '</td>' +
                        '<td class="text-right">' + line.total_purchase_qty + '</td>' +
                        '<td class="text-right">' + line.total_sales + '</td>' +
                        '<td class="text-right">' + line.total_profit + '</td>' +
                        '<td class="text-right">' + line.total_sales_qty + '</td>' +
                        '<td class="text-right">' + line.cost_of_sales + '</td>' +
                        '<td class="text-right">' + line.purchase_vs_cost_of_sales + '</td>' +
                        '<td class="text-right">' + line.profit_margin + '</td>' +
                        '<td class="text-right">' + line.sell_through + '</td>' +
                        '<td class="text-right">' + line.abc_classification + '</td>' +
                        '<td class="text-right">' + line.pack_size + '</td>' +
                        '<td class="text-left">' + line.sex + '</td>' +
                        '<td class="text-left">' + line.flower_type + '</td>' +
                        '<td class="text-left">' + line.create_date + '</td>' +
                        '<td class="text-left">' + line.last_sale_date + '</td>' +
                        '<td class="text-left">' + line.last_receipt_or_kit_assembly_date + '</td>' +
                        '<td class="text-left">' + line.product_group_category + '</td>' +
                        '</tr>'
                });
                tableBodyText += '<tr>' +
                    '<th class="text-right" colspan="3">Total</th>' +
                    '<th class="text-right">' + data.total.total_inv_val +
                    '<th class="text-right">' + data.total.total_ideal_inv_val + '</th>' +
                    '<th class="text-right">' + data.total.total_inv_val_v_ideal_inv_val + '</th>' +
                    '<th class="text-right">' + data.total.total_purchases + '</th>' +
                    '<th class="text-right">' + data.total.total_purchase_qty + '</th>' +
                    '<th class="text-right">' + data.total.total_sales + '</th>' +
                    '<th class="text-right">' + data.total.total_profit + '</th>' +
                    '<th class="text-right">' + data.total.total_sales_qty + '</th>' +
                    '<th class="text-right">' + data.total.total_cost_of_sales + '</th>' +
                    '<th class="text-right">' + data.total.total_purchases_vs_cost_of_sales + '</th>' +
                    '<th class="text-right">' + data.total.profit_margin_total + '</th>' +
                    '<th class="text-right">' + data.total.sell_through_total + '</th>' +
                    '<th class="text-right"/>'+
                    '<th class="text-right"/>' +
                    '<th class="text-right"/>' +
                    '<th class="text-right"/>' +
                    '<th class="text-right"/>' +
                    '<th class="text-right"/>' +
                    '<th class="text-right"/>' +
                    '<th class="text-right"/>' +
                    '</tr>'
                $('.sales-of-brand-table-tbody').html(tableBodyText);
            })
        },

        /**
         * @private
         * Prepare seedsman sales by product bar chart with data
         */
        _prepareSeedsmanSalesByProductBarChart: function () {
            let self = this;
            this._rpc({
                route: '/tgr/dashboard/get_seedsman_sales_by_product_barchart_data',
                params: {
                    start_date: this.startDate,
                    end_date: this.endDate,
                    country: $('#country').val(),
                    brand: $('#brand').val(),
                    warehouse: $('#warehouse').val(),
                },
            }).then(function (data) {
                // Increase spacing between legend and chart
                data.plugins = self._increaseSpacingBetweenLegendAndChart()
                // Render area chart
                let seedsmanSalesByProductBarChart = new Chart($('#seedsmanSalesByProductBarChart'), data);
                seedsmanSalesByProductBarChart.render()
            });
        },

        _getMultiSelectOptions: function (placeholder, search) {
            return {
                columns: 1,
                selectAll: true,
                texts: {
                    placeholder: placeholder,
                    search: search
                },
                search: true,
            }
        },

        /**
         * @private
         * Prepare filter values
         */
        _prepareFilterValues: function () {
            let self = this;
            this._rpc({
                route: '/tgr/dashboard/get_filter_values',
                params: {
                    purchase: true
                }
            }).then(function (data) {
                // Countries
                data.countries.forEach(function (country) {
                    $('#country').append($('<option>', {
                        value: country.id,
                        text : country.name
                    }));
                });
                // Initialize multi select
                $('#country').multiselect(self._getMultiSelectOptions('Select Country', 'Search Countries'));
                // Brands
                data.brands.forEach(function (brand) {
                    $('#brand').append($('<option>', {
                        value: brand.id,
                        text : brand.name
                    }));
                })
                // Initialize multi select
                $('#brand').multiselect(self._getMultiSelectOptions('Select Brand', 'Search Brand'));
                // Warehouses
                data.warehouses.forEach(function (warehouse) {
                    $('#warehouse').append($('<option>', {
                        value: warehouse.id,
                        text : warehouse.name
                    }));
                })
                // Initialize multi select
                $('#warehouse').multiselect(self._getMultiSelectOptions('Select Warehouse', 'Search Warehouse'));
                // Warehouses
                data.company.forEach(function (company) {
                    $('#company').append($('<option>', {
                        value: company.id,
                        text : company.name
                    }));
                })
                // Initialize multi select
                $('#company').multiselect(self._getMultiSelectOptions('Select Company', 'Search Company'));
            });
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
            this.startDateSOB = moment().startOf('year');
            this.endDateSOB = moment().endOf('year');
            this.dateInitializedSOB = true;
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
         * Update sob table data when onchange date
         */
        _onchangeSOBDate: function (start_date, end_date) {
            this.startDateSOB = start_date;
            this.endDateSOB = end_date;
            this._updateChartData();
            this.dateInitializedSOB = false;
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
         * Prepare date range for sales of brand
         */
        _prepareDateRangeSOB: function () {
            let start = moment().startOf('month');
            let end = moment().endOf('month');
            let self = this;
            function cb(start, end) {
                $('#sob-create-date-range #sob-load-data').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
                self._onchangeSOBDate(start, end)
            }
            $('#sob-create-date-range').daterangepicker({
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

        _prepareSOBFilterValues: function () {
            let self = this;
            this._rpc({
                route: '/tgr/dashboard/get_sob_filter_values',
            }).then(function (data) {
                // Brands
                data.brands.forEach(function (brand) {
                    $('#sob-brand').append($('<option>', {
                        value: brand.id,
                        text : brand.name
                    }));
                })
                // ABC Classification
                data.abc_classification.forEach(function (brand) {
                    $('#sob-abc-classification').append($('<option>', {
                        value: brand.id,
                        text : brand.name
                    }));
                })
                // Sex
                data.sex.forEach(function (brand) {
                    $('#sob-sex').append($('<option>', {
                        value: brand.id,
                        text : brand.name
                    }));
                })
                // Flowering Type
                data.flowering_type.forEach(function (brand) {
                    $('#sob-flowering-type').append($('<option>', {
                        value: brand.id,
                        text : brand.name
                    }));
                })
                // Odoo product tag
                data.product_tag.forEach(function (brand) {
                    $('#sob-odoo-product-tag').append($('<option>', {
                        value: brand.id,
                        text : brand.name
                    }));
                })
                // Odoo Product Group Category
                data.product_categ.forEach(function (brand) {
                    $('#sob-product-group-category').append($('<option>', {
                        value: brand.id,
                        text : brand.name
                    }));
                })
                // Odoo Product Segment
                data.product_segment.forEach(function (brand) {
                    $('#sob-product-segment').append($('<option>', {
                        value: brand.id,
                        text : brand.name
                    }));
                })
                // Warehouses
                data.warehouses.forEach(function (warehouse) {
                    $('#sob-warehouse').append($('<option>', {
                        value: warehouse.id,
                        text : warehouse.name
                    }));
                })
                // Website
                data.website.forEach(function (warehouse) {
                    $('#sob-website').append($('<option>', {
                        value: warehouse.id,
                        text : warehouse.name
                    }));
                })
                // Region
                data.region.forEach(function (warehouse) {
                    $('#sob-region').append($('<option>', {
                        value: warehouse.id,
                        text : warehouse.name
                    }));
                })
                // Countries
                data.countries.forEach(function (country) {
                    $('#sob-country').append($('<option>', {
                        value: country.id,
                        text : country.name
                    }));
                });
                data.company.forEach(function (company) {
                    $('#sob-company').append($('<option>', {
                        value: company.id,
                        text : company.name
                    }));
                });
                $('#sob-brand').multiselect(self._getMultiSelectOptions('Select Brand', 'Search Brand'));
                $('#sob-abc-classification').multiselect(self._getMultiSelectOptions('Select Classification', 'Search Classification'));
                $('#sob-sex').multiselect(self._getMultiSelectOptions('Select Sex', 'Search Sex'));
                $('#sob-flowering-type').multiselect(self._getMultiSelectOptions('Select Flowering Type', 'Search Flowering Type'));
                $('#sob-odoo-product-tag').multiselect(self._getMultiSelectOptions('Select Product Tag', 'Search Product Tag'));
                $('#sob-product-group-category').multiselect(self._getMultiSelectOptions('Select Product Category', 'Search Product Category'));
                $('#sob-product-segment').multiselect(self._getMultiSelectOptions('Select Product Segment', 'Search Product Segment'));
                $('#sob-warehouse').multiselect(self._getMultiSelectOptions('Select Warehouse', 'Search Warehouse'));
                $('#sob-website').multiselect(self._getMultiSelectOptions('Select Website', 'Search Website'));
                $('#sob-region').multiselect(self._getMultiSelectOptions('Select Region', 'Search Region'));
                $('#sob-country').multiselect(self._getMultiSelectOptions('Select Country', 'Search Country'));
                $('#sob-company').multiselect(self._getMultiSelectOptions('Select Company', 'Search Company'));
            });
        },

        /**
         * @override
         * Initialize charts, filters
         */
        on_attach_callback: function () {
            this._super();
            this._prepareDateRange();
            this._prepareFilterValues();
            this._prepareCurrentStockLevels();
            this._preparePurchaseCogsLineChart();
            this._preparePurchaseStockValueBarChart();
            this._prepareSellThroughRateLineChart();
            this._prepareSalesOfBrandTable();
            this._prepareSeedsmanSalesByProductBarChart();
            this._prepareDateRangeSOB();
            this._prepareSOBFilterValues();
        },

    });

    // load client action
    core.action_registry.add('tgr_purchase_dashboard', tgrPurchaseDashboard);

    return {
        MainMenu: tgrPurchaseDashboard,
    };

});
