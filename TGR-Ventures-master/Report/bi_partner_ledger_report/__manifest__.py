{
    "name": "Bi Partner Ledger Report",
    "version": "1.0",
    "category": "Module  Installation",
    "summary": "Module  Installation",
    "description": """Module  Installation""",
    "author": "Bassam Infotech LLP",
    "license": "OPL-1",
    "website": "http://www.bassaminfotech.com",
    "depends": ["base","account_reports"],
    "data": [
        "views/account_report_search.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/bi_partner_ledger_report/static/src/js/account_reports_filter.js",
        ],
    },
}
