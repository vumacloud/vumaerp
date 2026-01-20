# -*- coding: utf-8 -*-
{
    'name': 'Ghana - Base Localization',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Ghana Base Localization Module',
    'description': """
Ghana Localization
==================

Base localization module for Ghana including:
- Ghana country data
- TIN (Taxpayer Identification Number) validation
- GRA (Ghana Revenue Authority) integration base
- Currency formatting (GHS - Ghana Cedi)
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
