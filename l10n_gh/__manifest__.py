# Part of VumaERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ghana - Accounting',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations/Account Charts',
    'summary': 'Ghana fiscal localization with IFRS chart of accounts',
    'description': """
Ghana Accounting Localization
=============================

This module provides the standard accounting features for Ghana:

Chart of Accounts
-----------------
Based on IFRS (International Financial Reporting Standards) as adopted
by the Institute of Chartered Accountants, Ghana (ICAG) since 2007.

Taxes (VAT Act 1151, effective January 2026)
--------------------------------------------
* VAT: 15% standard rate
* NHIL: 2.5% (National Health Insurance Levy) - Input deductible
* GETFund: 2.5% (Ghana Education Trust Fund Levy) - Input deductible
* Total effective rate: 20%
* Zero-rated: Exports and specified supplies
* Exempt: Basic necessities, education, health

Fiscal Positions
----------------
* Domestic (standard 20% total)
* Export (zero-rated)
* Exempt supplies

Currency
--------
* GHS - Ghana Cedi

Regulatory Framework
--------------------
* Companies Act, 2019 (Act 992)
* Value Added Tax Act, 2025 (Act 1151)
* Ghana Revenue Authority (GRA) compliance

References:
- ICAG: https://icagh.com
- GRA: https://gra.gov.gh
- IFRS Ghana: https://www.ifrs.org/use-around-the-world/use-of-ifrs-standards-by-jurisdiction/view-jurisdiction/ghana/
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'data/account_chart_template_data.xml',
        'data/account_account_tag_data.xml',
        'data/account_account_template_data.xml',
        'data/account_tax_group_data.xml',
        'data/account_tax_template_data.xml',
        'data/account_fiscal_position_template_data.xml',
        'data/account_chart_template_configure_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
