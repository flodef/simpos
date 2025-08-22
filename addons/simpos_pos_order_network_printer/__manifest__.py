# -*- coding: utf-8 -*-
{
    'name': "Simpos Order Network Printer",

    'summary': """
        Simpos Order Network Printer""",

    'description': """
        Simpos Order Network Printer
    """,

    'author': "Hieu Tran",
    'website': "http://www.youngtailors.com",
    'category': 'Uncategorized',
    'license': 'LGPL-3',
    'version': '18.0.1.0',
    'depends': ['pos_restaurant'],

    'assets': {
        'point_of_sale.assets': [
            'simpos_pos_order_network_printer/static/src/js/*.js',
            'simpos_pos_order_network_printer/static/src/xml/*.xml',
        ],
    },
    'data': [
        'views/views.xml',
        'views/pos_restaurant_views.xml',
    ],
}
