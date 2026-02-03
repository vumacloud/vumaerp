# -*- coding: utf-8 -*-
{
    'name': 'Ghana - Accounting',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Ghana base localization',
    'description': """
Ghana Accounting Localization
=============================

Base localization for Ghana including:
- Ghana regions data
- TIN validation support
- Currency: GHS (Ghana Cedi)

Tax rates under VAT Act 1151 (effective January 2026):
- VAT: 15%
- NHIL: 2.5% (input deductible)
- GETFund: 2.5% (input deductible)
- Total effective rate: 20%

References:
- GRA: https://gra.gov.gh
- ICAG: https://icagh.com
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'data/res_country_data.xml',
        'data/template/account.group-gh.csv',
        'data/template/account.account-gh.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
