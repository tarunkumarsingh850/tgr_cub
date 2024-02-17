{
    "name": "material request form import",
    "summary": """
       Module is used to update the material request form import.
    """,
    "description": """
       Module is used to update the material request form import
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Purchase",
    "version": "15.0.1.0.1",
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "depends": ["bi_material_request_form", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "views/material_request.xml",
        "wizard/material_wizard.xml",
    ],
}
