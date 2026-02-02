# Part of VumaERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ghana - E-VAT Integration',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Ghana Revenue Authority E-VAT electronic invoicing integration',
    'description': """
Ghana E-VAT Integration Module
==============================

This module integrates with the Ghana Revenue Authority (GRA) E-VAT system
for electronic invoicing compliance under VAT Act 1151.

Features
--------
* Submit sales invoices to GRA Virtual Sales Data Controller (VSDC)
* Receive SDC codes and QR codes for fiscal receipts
* Support for all GRA tax codes (TAX_A through TAX_E)
* Support for levy codes (NHIL, GETFund, Tourism/CST)
* Sandbox and Production environment support

Tax Rates (VAT Act 1151, effective January 2026)
------------------------------------------------
* VAT (TAX_B): 15%
* NHIL (LEVY_A): 2.5% - Input deductible
* GETFund (LEVY_B): 2.5% - Input deductible
* Tourism/CST (LEVY_D): 1%/5%
* Total effective rate: 20%

Tax Code Mappings
-----------------
* TAX_A: 0% - Exempted supplies
* TAX_B: 15% - Standard taxable supplies
* TAX_C: 0% - Export (zero-rated)
* TAX_D: 0% - Non-taxable supplies
* TAX_E: 3% - Non-VAT flat rate

Requirements
------------
* VAT-registered business with GRA
* E-VAT credentials (TIN, Security Key)
* Completed GRA certification process

For more information, visit: https://gra.gov.gh/e-services/e-vat/
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'data/evat_tax_code_data.xml',
        'views/menu.xml',
        'views/evat_config_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
