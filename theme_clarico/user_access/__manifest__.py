{
    #Module information
    'name': 'User Access',
    'category': 'eCommerce',
    'summary': 'This app contains part of user access roles and restriction',
    'version': '1.0.0',
    'license': 'OPL-1',
    'depends':['website_sale_wishlist','website_sale_comparison'],

    'data': [
        'views/res_config_settings_views.xml',
        'views/res_users_view.xml',
	'views/product_template_view.xml',
        'templates/signup_confirmation_template.xml',
        'templates/website_sale_template.xml',
        'data/signup_confirmation_data.xml',
        'templates/assets.xml',
    ],

    #Odoo Store Specific
    'images': [
    ],

    # Author
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'https://www.emiprotechnologies.com',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',

    # Technical
    'installable': True,
    'auto_install': False,
}
