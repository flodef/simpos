# -*- coding: utf-8 -*-
{
    'name': "Simpos Vibration Cards",

    'summary': """
        Simpos Vibration Cards""",

    'description': """
        Simpos Vibration Cards
    """,

    'author': "Hieu Tran",
    'website': "http://youngtailors.com",

    'category': 'Uncategorized',
    'version': '0.1',

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
