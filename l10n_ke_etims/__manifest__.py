# -*- coding: utf-8 -*-
{
    'name': 'Kenya eTIMS Integration',
    'version': '17.0.2.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'KRA eTIMS OSCU integration for Kenya',
    'description': """
Kenya eTIMS OSCU Integration for Odoo 17

Compliant with KRA eTIMS requirements including:
- OSCU (Online Sales Control Unit) device initialization
- UNSPSC product classification codes
- Product registration with KRA
- Automatic stock movement reporting
- Invoice submission to KRA eTIMS
- SCU (Signed Code Unit) receipt numbers

Features:
- Fetch and manage KRA standard codes (OSCU codes)
- UNSPSC classification management for products
- Product registration with eTIMS before sales
- Automatic stock move reporting to eTIMS
- Sales invoice submission with digital signatures
- Multi-branch support with branch IDs

Based on official Odoo 17 Kenya localization standards.
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'product',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/etims_cron.xml',
        'views/etims_config_views.xml',
        'views/etims_code_views.xml',
        'views/product_views.xml',
        'views/stock_views.xml',
        'views/account_move_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
