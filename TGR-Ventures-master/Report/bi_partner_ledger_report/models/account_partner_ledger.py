from odoo import models, api


class ReportPartnerLedger(models.AbstractModel):
    _inherit = "account.partner.ledger"


    def _get_columns_name(self, options):
        res = super(ReportPartnerLedger, self)._get_columns_name(options)
        res.insert(6, {'name':'Responsible Salesperson'})
        return res
    

    @api.model
    def _get_report_line_partner(self, options, partner, initial_balance, debit, credit, balance):
        res = super(ReportPartnerLedger, self)._get_report_line_partner(options, partner, initial_balance, debit, credit, balance)
        if 'columns' in res and partner:
            res['columns'].insert(0,{'name': partner.user_id.name or ''})
        return res
    

    filter_salesperson = True

    @api.model
    def _get_options_domain(self, options):
        domain = super(ReportPartnerLedger, self)._get_options_domain(options)
        if options.get("salesperson"):
            if options.get("user_id"):
                domain += [("partner_id.user_id", "in", options["user_id"])]
        return domain