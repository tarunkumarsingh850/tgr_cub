odoo.define('bi_kit_specification_import.kit_tree_button', function (require) {
    "use strict";
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var TreeButton = ListController.extend({
       buttons_template: 'bi_kit_specification_import.buttons',
       events: _.extend({}, ListController.prototype.events, {
           'click .open_kit_wizard_action': '_OpenWizard',
       }),
       _OpenWizard: function () {
           var self = this;
            this.do_action({
               type: 'ir.actions.act_window',
               res_model: 'bill.material.wizard',
               name :'Import Kit Specification',
               view_mode: 'form',
               view_type: 'form',
               views: [[false, 'form']],
               target: 'new',
               res_id: false,
           });
       }
    });
    var KitListView = ListView.extend({
       config: _.extend({}, ListView.prototype.config, {
           Controller: TreeButton,
       }),
    });
    viewRegistry.add('button_in_tree_kit', KitListView);
    });
