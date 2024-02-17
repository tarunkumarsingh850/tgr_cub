odoo.define('bi_dynamic_sale_report.category_wise_report', function (require) {
'use strict';

var core = require('web.core');
var framework = require('web.framework');
var stock_report_generic = require('stock.stock_report_generic');

var QWeb = core.qweb;
var _t = core._t;

var AnalysisReport = stock_report_generic.extend({
    events: {
        'click .o_item_action': '_onClickAction',
    },
    get_html: function() {
        var self = this;
        var wizard = this.given_context.active_id;
        var args = [wizard];
        return this._rpc({
                model: 'report.bi_dynamic_sale_report.sale_order_report',
                method: 'get_html',
                args: args,
                context: this.given_context,
            })
            .then(function (result) {
                self.data = result;
            });
    },
    set_html: function() {
        var self = this;
        return this._super().then(function () {
            self.$el.html(self.data.lines);
            self.renderSearch();
            self.update_cp();
        });
    },
    render_html: function(event, $el, result){
        $el.after(result);
        $(event.currentTarget).toggleClass('o_mrp_bom_foldable o_mrp_bom_unfoldable fa-caret-right fa-caret-down');
        this._reload_report_type();
    },
    update_cp: function () {
        var status = {
            cp_content: {
                $buttons: this.$buttonPrint,
                $searchview: this.$searchView
            },
        };
        return this.updateControlPanel(status);
    },
    renderSearch: function () {
        this.$buttonPrint = $(QWeb.render('report.print'));
        this.$buttonPrint.filter('.o_item_report_xlsx').on('click', this._onClickPrintXlsx.bind(this));
    },
    _onClickPrintXlsx : function(ev){
      ev.preventDefault();
      var self = this;
      self._rpc({
          model: 'report.bi_dynamic_sale_report.sale_order_report',
          method: 'get_report_datas',
          args: [this.given_context.active_id],
         }).then(function(data){
        var action = {
              'type': 'ir.actions.report',
              'report_type': 'xlsx',
              'report_name': 'bi_dynamic_sale_report.report_sale_dynamic',
              'report_file': 'bi_dynamic_sale_report.report_sale_dynamic',
              'data': {'lines':data},
              'context': {
          //     'landscape':1,
              'from_js': true
          },
          'display_name': 'Analysis Report',
        };
      return self.do_action(action);
      });
      },
    _reload_report_type: function () {
        this.$('.o_mrp_bom_cost.o_hidden').toggleClass('o_hidden');
    },
    _onClickAction: function (ev) {
        ev.preventDefault();
        return this.do_action({
            type: 'ir.actions.act_window',
            res_model: $(ev.currentTarget).data('model'),
            res_id: $(ev.currentTarget).data('res-id'),
            views: [[false, 'form']],
            target: 'current'
        });
    },
});

core.action_registry.add('category_wise_report', AnalysisReport);
return AnalysisReport;

});
