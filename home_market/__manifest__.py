{
    'name': 'Home Market',
    'version': '1.0',
    'summary': 'Custom module for Home Market',
    'description': 'Add custom fields and functionality for Home Market',
    'author': 'Muhammad Mahmoud',
    'website': 'http://www.arch-sys.com',
    'depends': ['base', 'base_setup', 'product', 'website', 'website_sale',
                'sale', 'theme_common', 'theme_loftspace', 'theme_real_estate'
                ],
    'external_dependencies': {
        'python': ['pandas', 'requests', 'beautifulsoup4', 'urllib3', 'selenium'],
    },
    'data': [
       
        'views/HomeMarket_views.xml',
        'views/product_category_url_views.xml',
        'views/track_prices_views.xml',
        'views/scheduled_action_scraper_views.xml',
        'views/website_product_template.xml',
        'views/product_public_category.xml',
        'views/menu_items.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_frontend': [
            # '/home_market/static/src/js/Category_snippet.js',
            
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'auto_install': True,
}
