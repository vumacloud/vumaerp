# -*- coding: utf-8 -*-
{
    'name': 'Kenya eTIMS Integration',
    # Version format: 17.0.{TIS_MAJOR}.{TIS_MINOR}.{TIS_PATCH}
    # - 17.0: Odoo version prefix (required by Odoo)
    # - TIS_MAJOR: Breaking changes or major KRA compliance updates
    # - TIS_MINOR: New features or KRA requirement additions
    # - TIS_PATCH: Bug fixes and minor improvements
    'version': '17.0.2.0.1',
    'category': 'Accounting/Localizations',
    'summary': 'VumaERP KRA eTIMS OSCU integration for Kenya',
    'description': """
VumaERP Kenya eTIMS Integration
===============================

Trader Invoicing System (TIS) for Kenya Revenue Authority (KRA) eTIMS compliance.

TIS IDENTIFICATION
------------------
- TIS Name: VumaERP
- TIS Version: 2.0.0
- Serial Number Format: VUMAERP{TIN}{BRANCH_ID}
  Example: VUMAERPP051234567A00

KRA eTIMS COMPLIANCE
--------------------
- OSCU (Online Sales Control Unit) device initialization
- UNSPSC product classification codes
- Product registration with KRA before sales
- Automatic stock movement reporting
- Invoice submission with digital signatures
- SCU (Signed Code Unit) receipt numbers
- Payment-triggered submission (KPMG advisory compliant)

FEATURES
--------
- Auto-generated device serial numbers (VUMAERP convention)
- Fetch and manage KRA standard codes (OSCU codes)
- UNSPSC classification management for products
- Multi-branch support with branch IDs
- Sandbox and Production environment support

VERSIONING
----------
Module version: 17.0.2.0.0 (Odoo 17.0, TIS v2.0.0)
KRA TIS Version: 2.0.0

For KRA registration, report TIS Version as: 2.0.0
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/etims_cron.xml',
        'data/etims_daily_report_data.xml',
        'views/etims_config_views.xml',
        'views/etims_code_views.xml',
        'views/etims_daily_report_views.xml',
        'views/product_views.xml',
        'views/account_move_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
