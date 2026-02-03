# -*- coding: utf-8 -*-
{
    'name': 'Ghana - Base',
    'version': '17.0.1.0.0',
    'category': 'Localization',
    'summary': 'Ghana base data (regions)',
    'description': """
Ghana Base Localization
=======================

Base data for Ghana including:
- Ghana's 16 administrative regions

This module provides foundational data for other Ghana-specific modules.
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'data/res_country_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
