{
    'name': 'Salon Portal Configuration',
    'version': '13.0.1.0.0',
    'summary': 'Salon Portal Configuration',
     'category': 'Salon',
    'author': 'Pandoratech',
    'maintainer': 'Pandoratech',
    'company': 'Pandora Desgin',
    'website': 'https://pandoratech.ae',
    'depends': [
        'odoo_marketplace','hr'
    ],
    'description': """
           Salon Portal Configuration
    """,
   'data': [
    'security/ir.model.access.csv',
    'views/res_partner.xml',
    'views/sale_order.xml',
    'views/product_template.xml',
   # 'reports/report_carhop.xml',
  #  'reports/report.xml'
    

],  

    'installable': True,
    'auto_install': False,
    'application': True,
}