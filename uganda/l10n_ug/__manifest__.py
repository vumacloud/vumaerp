# -*- coding: utf-8 -*-
{
    'name': 'Uganda - Base Localization',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Base module for Uganda localization',
    'description': """
Uganda Base Localization
========================

This module provides the base localization for Uganda including:
- Country-specific data and formats
- URA (Uganda Revenue Authority) compliance foundation
- Currency formatting (UGX - Ugandan Shilling)

This is a dependency for other Uganda-specific modules like:
- l10n_ug_efris: URA EFRIS e-invoicing
- l10n_ug_payroll: Uganda payroll (PAYE, NSSF, LST)
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'Other proprietary',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/res_country_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
