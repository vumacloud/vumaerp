# -*- coding: utf-8 -*-
{
    'name': 'KRA e-TIMS Integration',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Kenya Revenue Authority e-TIMS (OSCU) Integration for Electronic Invoicing',
    'description': """
KRA e-TIMS Integration for Odoo v17
====================================

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
