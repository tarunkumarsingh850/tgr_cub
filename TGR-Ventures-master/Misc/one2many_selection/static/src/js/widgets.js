odoo.define('web_one2many_selectable_10.form_widgets', function (require) {
    "use strict";

    var core = require('web.core');
    var utils = require('web.utils');
    var _t = core._t;
    var QWeb = core.qweb;
    var Dialog = require('web.Dialog');
    var fieldRegistry = require('web.field_registry');
    var ListRenderer = require('web.ListRenderer');
    var rpc = require('web.rpc');
    var FieldOne2Many = require('web.relational_fields').FieldOne2Many;

    ListRenderer.include({

        // Override this method to get delete button appear,disappear logic
        _updateSelection: function () {
            this.selection = [];
            var self = this;
            var $inputs = this.$('tbody .o_list_record_selector input:visible:not(:disabled)');
            var allChecked = $inputs.length > 0;
            $inputs.each(function (index, input) {
                if (input.checked) {
                    self.selection.push($(input).closest('tr').data('id'));
                } else {
                    allChecked = false;
                }
            });
            if(this.selection.length > 0){
                $('.button_create_po_agreement').show()
            }else{
                $('.button_create_po_agreement').hide()
            }
            this.$('thead .o_list_record_selector input').prop('checked', allChecked);
            this.trigger_up('selection_changed', { selection: this.selection });
            this._updateFooter();
        },
    })


    var One2ManySelectable = FieldOne2Many.extend({
        template: 'One2ManySelectable',
        events: {
            "click .button_create_po_agreement": "action_selected_lines",
        },
        start: function()
        {
            this._super.apply(this, arguments);
            var self=this;
       },
        //passing ids to function
        action_selected_lines: function()
        {
            var self = this;
              var selected_ids = self.get_selected_ids_one2many();
              if (selected_ids.length === 0) {
                this.do_warn(_t("You must choose at least one record."));
                return false;
              }
              rpc.query({
              model: "sale.order",
              method: "create_purchase_wizard",
              args: [selected_ids],
            }).then(function (result) {
                if (result){
                    if (result['error']) {
                        alert("You Can't create purchase order!");
                    }else {
                    self.do_action({
                        type: "ir.actions.act_window",
                        name: "Create Purchase",
                        res_model: "purchase.wizard",
                        views: [[false, "form"]],
                        context: {
                        default_enquiry_number:self.recordData.enquiry_number,
                        default_sale_id: self.recordData.id,
                        default_agreement_line_ids: result.line_ids,
                        },
                        target: "new",
                    });
                }
            }
                else {
                    Dialog.alert(self, '', {
                    title: _t("Server error"),
                    $content: $('<div/>').html(
                        _t("You Can't Create Purchase order in This State.")
                        + '<br/>'
                    )
                });
                }
            });
        },
        _getRenderer: function () {
            if (this.view.arch.tag === 'kanban') {
                return One2ManyKanbanRenderer;
            }
            if (this.view.arch.tag === 'tree') {
                return ListRenderer.extend({
                    init: function (parent, state, params) {
                        this._super.apply(this, arguments);
                        this.hasSelectors = true;
                    },
                });
            }
            return this._super.apply(this, arguments);
        },
        //collecting the selected IDS from one2manay list
        get_selected_ids_one2many: function () {
            var self=this;
            var ids =[];
            this.$el.find('td.o_list_record_selector input:checked')
                    .closest('tr').each(function () {
                        ids.push(parseInt(self._getResId($(this).data('id'))));
            });
            return ids;
        },

        _getResId: function (recordId) {
            var record;
            utils.traverse_records(this.recordData[this.name], function (r) {
                if (r.id === recordId) {
                    record = r;
                }
            });
            return record.res_id;
        },

    });
    // register unique widget, because Odoo does not know anything about it
    //you can use <field name="One2many_ids" widget="x2many_selectable"> for call this widget
    fieldRegistry.add('one2many_selectable', One2ManySelectable);
});
