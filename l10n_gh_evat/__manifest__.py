# -*- coding: utf-8 -*-
{
    'name': 'Ghana - E-VAT Integration',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'GRA E-VAT electronic invoicing for Ghana',
    'description': """
Ghana GRA E-VAT Integration (API v8.2)
======================================

Integration with Ghana Revenue Authority E-VAT system for electronic invoicing
under VAT Act 1151.

Features:
- Submit sales invoices to GRA VSDC
- Submit POS receipts to GRA E-VAT automatically
- Receive SDC codes and QR codes
- Print E-VAT compliant receipts from POS
- Track submission status
- TIN validation via GRA API

IMPORTANT - Tax Setup (GRA Best Practice):
------------------------------------------
Per GRA requirements, invoices must show taxes SEPARATELY:

1. VAT 15% (Sales) - Standard Value Added Tax
2. NHIL 2.5% (Sales) - National Health Insurance Levy
3. GETFund 2.5% (Sales) - Ghana Education Trust Fund Levy

Total effective rate: 20%

To configure products correctly:
- Go to product form > Sales tab
- Select ALL THREE taxes: VAT 15%, NHIL 2.5%, GETFund 2.5%

Additional sector-specific taxes:
- CST 5% - Communication Service Tax (telecom)
- Tourism 1% - Tourism levy (hospitality)

Tax Calculation:
- All taxes/levies calculated on the BASE amount (before other taxes)
- Invoice shows: Subtotal + NHIL + GETFund + VAT = Total

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
