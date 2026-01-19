# -*- coding: utf-8 -*-
{
    'name': 'Ethiopia - Base Localization',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Base localization module for Ethiopia',
    'description': """
Ethiopia Base Localization
==========================

This module provides the base localization for Ethiopia including:
- Ethiopia country data
- Currency (ETB - Ethiopian Birr)
- Regional configurations
- Base compliance structures

This is the foundation module for all Ethiopia-specific Odoo customizations.
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'Other proprietary',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/res_country_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
