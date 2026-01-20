# -*- coding: utf-8 -*-
{
    'name': 'Nigeria - Base Localization',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Nigeria Base Localization Module',
    'description': """
Nigeria Localization
====================

Base localization module for Nigeria including:
- Nigeria country data and states
- TIN (Tax Identification Number) validation
- FIRS (Federal Inland Revenue Service) integration base
- Currency formatting (NGN - Nigerian Naira)
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
