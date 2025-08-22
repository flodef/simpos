# -*- coding: utf-8 -*-
{
    'name': 'SIMPOS Vibration Card',
    'summary': 'Vibration payment card support for SIMPOS',
    'description': """
        Simpos Vibration Cards
    """,
    'version': '1.0.0.0',
    'author': 'FIMS Integrated Management Systems Oy',
    'website': 'https://fims.fi',
    'category': 'Point of Sale',
    'license': 'LGPL-3',
    'depends': ['point_of_sale'],

    'data': [
        'views/views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'simpos_vibration_card/static/src/js/*.js',
            'simpos_vibration_card/static/src/xml/*.xml',
        ],
    },

}
