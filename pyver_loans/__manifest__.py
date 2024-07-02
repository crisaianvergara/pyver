{
    "name": "Loans",
    "summary": """Loans""",
    "description": """Loans""",
    "author": "Cris-aian Vergara",
    "website": "https://www.crisaianvergara.com",
    "category": "Loans",
    "version": "17.0.1.0.0",
    "depends": ["base", "mail", "account",],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",

        "data/loans_data.xml",

        "views/loans_menus.xml",
        "views/loan_request_views.xml",
        "views/loan_type_views.xml",
        "views/res_config_settings_views.xml",
        
        'report/loan_request_templates.xml',
        'report/loan_request_reports.xml',
    ],
    "demo": [],
    "assets": {},
    "sequence": -100,
    "application": True,
    "installable": True,
    "license": "LGPL-3"
}