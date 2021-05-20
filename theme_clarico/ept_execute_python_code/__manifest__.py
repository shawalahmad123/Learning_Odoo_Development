{
    "name": "Execute Python Code",
    "description": """Installing this module, user will able to execute python code from OpenERP""",
    "author": "OpenERP SA",
    "version": "1.0",
    'license': 'OPL-1',
    "depends": ["base"],
    "init_xml": [],
    "data": [
        'security/ir.model.access.csv',
        'view/python_code_view.xml',
        'view/cron_code_execute.xml',
    ],
    "demo_xml": [],
    "installable": True,
}
