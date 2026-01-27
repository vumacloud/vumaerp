# -*- coding: utf-8 -*-
{

This module integrates Odoo with Kenya Revenue Authority's electronic Tax Invoice
Management System (eTIMS) via the Online Sales Control Unit (OSCU) API.

Features:
---------
* Device registration and verification
* Real-time invoice transmission to KRA
* Item classification and registration
* Customer PIN validation
* Stock movement reporting
* Purchase and sales transaction submission
* Multi-branch support

API Endpoints Implemented:
--------------------------
* DeviceVerificationReq - Device authentication
* CodeSearchReq - Code lookups
* CustSearchReq - Customer validation
* ItemClsSearchReq - Item classification codes
* ItemSaveReq / ItemSearchReq - Item management
* BhfSearchReq - Branch information
* BhfCustSaveReq / BhfUserSaveReq - Branch management
* TrnsSalesSaveWrReq - Sales transaction submission
* TrnsPurchaseSalesReq / TrnsPurchaseSaveReq - Purchase management
* StockMoveReq / StockIOSaveReq / StockMasterSaveReq - Inventory management

Configuration:
--------------
* Sandbox URL: https://etims-api-sbx.kra.go.ke
* Production URL: https://etims-api.kra.go.ke/etims-api
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'Other proprietary',
    'depends': [
        'base',
        'mail',
        'om_account_accountant',
        'stock',
        'sale',
        'purchase',
        'l10n_ke',
    ],
    'data': [
        'security/etims_security.xml',
        'security/ir.model.access.csv',
        'data/etims_code_data.xml',
        'views/etims_config_views.xml',
        'views/etims_device_views.xml',
        'views/etims_code_views.xml',
        'views/account_move_views.xml',
        'views/product_views.xml',
        'views/res_partner_views.xml',
        'wizards/etims_customer_info_wizard_views.xml',
        'views/etims_menu.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'name': 'KRA e-TIMS Integration',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Kenya Revenue Authority e-TIMS (OSCU) Integration for Electronic Invoicing',
    'description': """
KRA e-TIMS Integration for Odoo v17

This module provides integration with Kenya Revenue Authority's e-TIMS (Tax Invoice Management System)
through the OSCU (Online Sales Control Unit) interface.

Features:
---------
* Generate and submit electronic invoices to KRA e-TIMS
* Automatic validation and compliance checks
* Support for different invoice types (Normal, Refund, Proforma)
* Item classification and tax type management
* Real-time status tracking and updates
* Support for B2B and B2C transactions
* Automatic stock movement reporting
* Device initialization and management
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'product',
        'uom',
        'sale',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/product_classification_data.xml',
        'data/tax_type_data.xml',
        'views/res_config_settings_views.xml',
        'views/account_move_views.xml',
        'views/product_template_views.xml',
        'views/res_partner_views.xml',
        'views/kra_etims_device_views.xml',
        'views/kra_etims_classification_views.xml',
        'views/kra_etims_menu.xml',
        'wizard/kra_etims_initialize_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
