# -*- coding: utf-8 -*-
{
    'name': 'Kenya - eTIMS Stock Integration',
    'version': '17.0.2.0.1',
    'category': 'Inventory/Localizations',
    'summary': 'VumaERP KRA eTIMS stock movement reporting',
    'description': """
Kenya eTIMS Stock/Inventory Integration
========================================

Extends the base Kenya eTIMS module with stock movement reporting.
Install this module if you use the Inventory (stock) module.

Features:
- Automatic stock movement reporting to KRA eTIMS
- Stock picking eTIMS status tracking
- Inventory level reporting
- Auto-report on stock move validation

This module requires both l10n_ke_etims and stock modules.
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': [
        'stock',
        'l10n_ke_etims',
    ],
    'data': [
        'data/etims_stock_cron.xml',
        'views/stock_views.xml',
    ],
    'installable': True,
    'auto_install': True,  # Auto-install when both stock and l10n_ke_etims are installed
    'application': False,
}
