# -*- coding: utf-8 -*-
{
    'name': 'Rwanda - Base Localization',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Base localization module for Rwanda',
    'description': """
Rwanda Base Localization
========================

This module provides the base localization for Rwanda including:
- Rwanda country data
- Currency (RWF - Rwandan Franc)
- Regional configurations
- Base compliance structures for RRA (Rwanda Revenue Authority)

This is the foundation module for all Rwanda-specific Odoo customizations.
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
