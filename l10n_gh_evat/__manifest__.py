# -*- coding: utf-8 -*-
{
    'name': 'Ghana - E-VAT Integration',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'GRA E-VAT electronic invoicing for Ghana',
    'description': """
Ghana GRA E-VAT Integration
===========================

Integration with Ghana Revenue Authority E-VAT system for electronic invoicing
under VAT Act 1151.

Features:
- Submit sales invoices to GRA VSDC
- Receive SDC codes and QR codes
- Track submission status

Tax Rates (VAT Act 1151, January 2026):
- VAT: 15%
- NHIL: 2.5%
- GETFund: 2.5%
- Total: 20%

Reference: https://gra.gov.gh/e-services/e-vat/
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'data/evat_tax_code_data.xml',
        'views/evat_config_views.xml',
        'views/account_move_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
