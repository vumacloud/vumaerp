# -*- coding: utf-8 -*-
{
    'name': 'Nigeria - FIRS Tax Integration',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Federal Inland Revenue Service Tax Integration',
    'description': """
Nigeria FIRS Tax Integration
============================

Integration with Federal Inland Revenue Service (FIRS) for tax compliance.

Features:
---------
* VAT (Value Added Tax) management at 7.5%
* WHT (Withholding Tax) calculations
* CIT (Company Income Tax) tracking
* TCC (Tax Clearance Certificate) management
* Electronic tax filing preparation

Nigeria Tax Rates (2025):
------------------------
* **VAT**: 7.5%
* **WHT**: 5-10% (depending on transaction type)
* **CIT**: 30% (large companies), 20% (medium), 0% (small)

FIRS Registration:
-----------------
* TIN (Tax Identification Number) required
* VAT registration for businesses with turnover > NGN 25 million
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'Other proprietary',
    'depends': [
        'account',
        'l10n_ng',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/tax_codes_data.xml',
        'views/firs_config_views.xml',
        'views/account_move_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
