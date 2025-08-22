# -*- coding: utf-8 -*-
{
    'name': "Simpos Receipt Network Printer",

    'summary': """
        Simpos Receipt Network Printer""",

    'description': """
        Simpos Receipt Network Printer
    """,
    'author': "Hieu Tran",
    'website': "http://www.youngtailors.com",
    'category': 'Uncategorized',
    'license': 'LGPL-3',
    'version': '18.0.1.0',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale.assets': [
            'simpos_receipt_network_printer/static/src/js/*.js',
        ],
    },
    'data': [
        'views/views.xml'
    ],
}
