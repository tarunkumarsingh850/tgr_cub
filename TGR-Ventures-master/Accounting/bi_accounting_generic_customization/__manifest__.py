{
    "name": "Accouting Module Customization",
    "summary": """
        Accouting Module Customization""",
    "description": """
        Accouting Module Customization
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Uncategorized",
    "version": "15.0.1",
    "depends": [
        "base",
        "account",
        "bi_customer_generic_customization",
        "bi_vendor_generic_customisation",
        "l10n_es_edi_sii",
        "l10n_es_reports",
        "bi_invoice_memo_printout",
    ],
    "data": [
        "security/account_move_security.xml",
        "data/cron.xml",
        "data/server_actions.xml",
        "data/mail_data.xml",
        "views/account_move.xml",
        "views/account_payment.xml",
        "views/account_tax.xml",
        "views/stock_warehouse.xml",
    ],
    "post_load": "post_load_hook",
}
