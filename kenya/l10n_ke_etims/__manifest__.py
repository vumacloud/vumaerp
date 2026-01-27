# -*- coding: utf-8 -*-
{
    'name': 'Kenya - eTIMS OSCU Integration',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'KRA eTIMS Online Sales Control Unit (OSCU) Integration',
    'description': """
Kenya eTIMS OSCU Integration
============================

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
}
