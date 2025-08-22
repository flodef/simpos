# -*- coding: utf-8 -*-
{
    'name': "Simpos Customer Display",

    'summary': """
        Simpos Customer Display""",

    'description': """
        Simpos Customer Display
    """,

    'author': "Hieu Tran",
    'website': "https://youngtailors.com",
    'category': 'Uncategorized',
    'license': 'LGPL-3',
    'version': '18.0.1.0',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale.assets': [
            'simpos_customer_display/static/src/js/*.js',
            'simpos_customer_display/static/src/xml/*.xml',
            'simpos_customer_display/static/src/css/*.css',
        ],
    },
    'data': [
        'views/views.xml'
    ],
}
