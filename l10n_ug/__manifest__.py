# -*- coding: utf-8 -*-
{
    'name': 'Uganda - Base Localization',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Base localization module for Uganda',
    'description': """
Uganda Base Localization
========================

This module provides the base localization for Uganda including:
- Uganda country data
- Currency (UGX - Ugandan Shilling)
- Regional configurations
- Base compliance structures

This is the foundation module for all Uganda-specific Odoo customizations.
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
