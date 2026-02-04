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
- Submit POS receipts to GRA E-VAT automatically
- Receive SDC codes and QR codes
- Print E-VAT compliant receipts from POS
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
    'depends': ['account', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/evat_tax_code_data.xml',
        'views/evat_config_views.xml',
        'views/account_move_views.xml',
        'views/pos_order_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'l10n_gh_evat/static/src/js/pos_receipt.js',
            'l10n_gh_evat/static/src/xml/pos_receipt.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
