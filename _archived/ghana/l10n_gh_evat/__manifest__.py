# -*- coding: utf-8 -*-
{
    'name': 'Ghana - GRA E-VAT',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Ghana Revenue Authority E-VAT Integration',
    'description': """
Ghana GRA E-VAT Integration
===========================

Integration with Ghana Revenue Authority E-VAT system for electronic invoicing.

Features:
---------
* E-VAT device registration
* Real-time invoice submission to GRA
* VAT return generation
* Tax code management (VAT, NHIL, GETFund, COVID Levy)

Ghana Tax Rates (2025):
----------------------
* **VAT**: 15%
* **NHIL**: 2.5% (National Health Insurance Levy)
* **GETFund**: 2.5% (Ghana Education Trust Fund)
* **COVID-19 Levy**: 1% (Health Recovery Levy)

Note: Effective combined rate is 21% for standard-rated supplies.
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'Other proprietary',
    'depends': [
        'om_account_accountant',
        'l10n_gh',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/evat_tax_codes_data.xml',
        'views/evat_config_views.xml',
        'views/account_move_views.xml',
        'wizard/evat_invoice_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
