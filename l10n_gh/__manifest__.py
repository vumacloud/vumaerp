# -*- coding: utf-8 -*-
{
    'name': 'Ghana - Accounting',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Ghana fiscal localization with VAT, NHIL, GETFund',
    'description': """
Ghana Fiscal Localization
=========================

Complete fiscal localization for Ghana including:

Chart of Accounts:
- IFRS-compliant chart of accounts for Ghana
- Accounts for VAT, NHIL, GETFund tracking

Tax Rates (VAT Act 1151, effective January 2026):
- VAT: 15% (standard rate)
- NHIL: 2.5% (National Health Insurance Levy)
- GETFund: 2.5% (Ghana Education Trust Fund)
- VAT Flat Rate: 3% (for qualifying retailers)
- Zero Rated: 0% (exports)
- Exempt: 0% (exempt supplies)

Total effective rate for standard supplies: 20%

References:
- Ghana Revenue Authority: https://gra.gov.gh
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
