# -*- coding: utf-8 -*-
{
    'name': 'Kenya - Base Localization',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Base localization module for Kenya',
    'description': """
Kenya Base Localization
=======================

This module provides the base localization for Kenya including:
- Kenya country data
- Currency (KES - Kenyan Shilling)
- Regional configurations
- Base compliance structures

This is the foundation module for all Kenya-specific Odoo customizations.
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
