{
    "name": "Logistics Report",
    "summary": """
        Logistics Report""",
    "description": """
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Sale",
    "version": "15.0.0.1",
    "depends": ["sale", "report_xlsx", "bi_sale_configuration"],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_template.xml",
        "data/cron.xml",
        "report/paperformact.xml",
        "report/logistics_report_pdf.xml",
        "report/report_action.xml",
        "view/logistic_scheduler.xml",
        "wizard/logistics_wizard.xml",
    ],
}
