odoo.define('tgr_dashboards.crm_dashboard', function (require) {
    "use strict";

    let AbstractAction = require('web.AbstractAction');
    let core = require('web.core');

    let tgrCrmDashboard = AbstractAction.extend({
        contentTemplate: 'tgrCrmDashboard',

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
            'change #salesperson': '_onchangeSalesPerson',
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
         * Change data when changing salesperson field
         */
        _onchangeSalesPerson: function () {
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
            }
            if (!this.dateInitialized) {
                // Update completed orders bar chart data
                let salespersonVsRevenue = Chart.getChart("salespersonVsRevenue")
                this._rpc({
                    route: '/tgr/dashboard/get_salesperson_vs_revenue_data',
                    params: params,
                }).then(function (data) {
                    salespersonVsRevenue.data.labels = data.data.labels;
                    salespersonVsRevenue.data.datasets = data.data.datasets;
                    salespersonVsRevenue.update();
                });
                // update leads information table
                this._prepareLeadsInformation();
                // update leads and conversions table
                this._prepareLeadsAndConversions();
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
                    // Multiple lines for labels
                    chart.data.labels.forEach(function(e, i, a) {
                        if (/\n/.test(e)) {
                            a[i] = e.split(/\n/);
                        }
                    });
                }
            }]
        },

        /**
         * @private
         * Prepare salesperson vs revenue area chart with data
         */
        _prepareaSalespersonVsRevenueAreaChart: function () {
            let self = this;
            this._rpc({
                route: '/tgr/dashboard/get_salesperson_vs_revenue_data',
                params: {
                    start_date: this.startDate,
                    end_date: this.endDate,
                    salesperson: $('#salesperson').val(),
                    country: $('#country').val(),
                },
            }).then(function (data) {
                // Increase spacing between legend and chart
                data.plugins = self._increaseSpacingBetweenLegendAndChart()
                // Render pie chart
                let salespersonVsRevenue = new Chart($('#salespersonVsRevenue'), data);
                salespersonVsRevenue.render()
            });
        },

        /**
         * @private
         * Prepare lead information data
         */
        _prepareLeadsInformation: function () {
            let params = {
                start_date: this.startDate,
                end_date: this.endDate,
                salesperson: $('#salesperson').val(),
                country: $('#country').val()
            }
            this._rpc({
                route: '/tgr/dashboard/prepare_leads_information',
                params: params,
            }).then(function (data) {
                let tableBodyText = '';
                data.lines.forEach(function(line) {
                    tableBodyText += '<tr><td class="text-left">' + line.customer_name + '</td><td>' + line.country_id + '</td></tr>'
                });
                $('.leads-information-tbody').html(tableBodyText);
            })
        },

        /**
         * @private
         * Prepare leads and conversions data
         */
        _prepareLeadsAndConversions: function () {
            let params = {
                start_date: this.startDate,
                end_date: this.endDate,
                salesperson: $('#salesperson').val(),
                country: $('#country').val()
            }
            this._rpc({
                route: '/tgr/dashboard/prepare_leads_and_conversions',
                params: params,
            }).then(function (data) {
                let tableBodyText = '';
                data.lines.forEach(function(line) {
                    tableBodyText +=
                        '<tr>' +
                        '<td class="center">' + line.salesperson + '</td>' +
                        '<td class="center">' + line.number_of_leads + '</td>' +
                        '<td class="center">' + line.new_leads + '</td>' +
                        '<td class="center">' + line.leads_converted_c + '</td>' +
                        '<td class="center">' + line.leads_converted_pc + '</td>' +
                        '<td class="center">' + line.total_revenue_from_converted_leads + '</td>' +
                        '<td class="center">' + line.total_revenue_from_new_customers + '</td>' +
                        '<td class="center">' + line.leads_to_purchase_conversion_rate + '</td>' +
                        '</tr>'
                });
                $('.crm-leads-and-conversions-tbody').html(tableBodyText);
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
            });
        },

        /**
         * @override
         * Initialize charts, filters
         */
        on_attach_callback: function () {
            this._prepareDateRange();
            this._prepareaSalespersonVsRevenueAreaChart();
            this._prepareFilterValues();
            this._prepareLeadsInformation();
            this._prepareLeadsAndConversions();
        }

    });

    // load client action
    core.action_registry.add('tgr_crm_dashboard', tgrCrmDashboard);

    return {
        MainMenu: tgrCrmDashboard,
    };

});
