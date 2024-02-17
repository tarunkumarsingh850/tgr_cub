{
    "name": "Purchase Customization",
    "summary": """
        Purchase Customization""",
    "description": """
        Purchase Customization
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Uncategorized",
    "version": "15.0.1",
    "post_load": "post_load_hook",
    "depends": ["base", "purchase", "partner_manual_rank"],
    "data": [
        "security/group.xml",
        "views/views.xml",
    ],
}
