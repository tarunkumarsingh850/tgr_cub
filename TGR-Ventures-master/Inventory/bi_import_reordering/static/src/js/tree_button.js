odoo.define('bi_import_reordering.tree_button', function (require) {
    "use strict";
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var TreeButton = ListController.extend({
       buttons_template: 'bi_import_reordering.buttons',
       events: _.extend({}, ListController.prototype.events, {
           'click .open_wizard_action': '_OpenWizard',
       }),
       _OpenWizard: function () {
           var self = this;
            this.do_action({
               type: 'ir.actions.act_window',
               res_model: 'import.reordering',
               name :'Import Reordering',
               view_mode: 'form',
               view_type: 'form',
               views: [[false, 'form']],
               target: 'new',
               res_id: false,
           });
       }
    });
    var ReplenishmentListView = ListView.extend({
       config: _.extend({}, ListView.prototype.config, {
           Controller: TreeButton,
       }),
    });
    viewRegistry.add('button_in_reorder_tree', ReplenishmentListView);
    });
