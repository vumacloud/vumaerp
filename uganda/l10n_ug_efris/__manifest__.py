# -*- coding: utf-8 -*-
{
    'name': 'Uganda - EFRIS Integration',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations/EDI',
    'summary': 'URA EFRIS Electronic Fiscal Receipting and Invoicing System',
    'description': """
Uganda EFRIS Integration
========================

This module integrates Odoo with Uganda Revenue Authority's EFRIS
(Electronic Fiscal Receipting and Invoicing System).

Features:
---------
* Device registration and management
* Real-time invoice submission to URA
* Automatic FDN (Fiscal Document Number) generation
* Credit note handling
* Stock management integration
* Goods/Services code mapping

EFRIS Requirements:
------------------
* Registered TIN with URA
* EFRIS device ID and credentials
* Valid SSL certificates
* Internet connectivity for API calls

Supported Document Types:
------------------------
* Sales Invoices (101)
* Credit Notes (102)
* Debit Notes (103)

API Endpoints:
-------------
* Device initialization
* Taxpayer information query
* Goods/Services code management
* Invoice upload
* Credit note upload
* Stock management
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'Other proprietary',
    'depends': [
        'om_account_accountant',
        'l10n_ug',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/efris_tax_codes_data.xml',
        'data/efris_document_type_data.xml',
        'views/efris_config_views.xml',
        'views/account_move_views.xml',
        'views/efris_device_views.xml',
        'wizard/efris_invoice_wizard_views.xml',
    ],
    'demo': [],
    'external_dependencies': {
        'python': ['requests', 'cryptography'],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
