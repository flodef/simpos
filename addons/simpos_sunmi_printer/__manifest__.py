# -*- coding: utf-8 -*-
{
    'name': "Simpos Sunmi Printer",

    'summary': """
        Simpos Sunmi Printer""",

    'description': """
        Simpos Receipt Network Printer
    """,
    'author': "Hieu Tran",
    'website': "http://www.youngtailors.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale.assets': [
            'simpos_sunmi_printer/static/src/js/*.js',
        ],
    },
    'data': [
        'views/views.xml'
    ],
}
