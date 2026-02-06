# -*- coding: utf-8 -*-
{
    'name': 'Kenya - eTIMS POS Integration',
    # Version format: 17.0.{TIS_MAJOR}.{TIS_MINOR}.{TIS_PATCH}
    # Must match base l10n_ke_etims module versioning
    'version': '17.0.2.0.0',
    'category': 'Point of Sale',
    'summary': 'VumaERP KRA eTIMS integration for Point of Sale',
    'description': """
VumaERP Kenya eTIMS POS & Payment Integration
=============================================

Part of VumaERP TIS (Trader Invoicing System) for KRA eTIMS compliance.

TIS IDENTIFICATION
------------------
- TIS Name: VumaERP
- TIS Version: 2.0.0
- Module Version: 17.0.2.0.0 (Odoo 17.0, TIS v2.0.0)

CRITICAL COMPLIANCE FEATURE
---------------------------
Submits to eTIMS only when payment is received, not when invoice is posted.
This aligns with KRA regulations and KPMG advisory that income in eTIMS
must represent actual sales transactions.

POS FEATURES
------------
* Real-time POS order submission to eTIMS at payment completion
* Batch submission at session close for any missed orders
* POS return/refund handling with KRA reason codes
* Session-level eTIMS submission tracking (submitted/pending/failed stats)
* eTIMS receipt printing with SCU and receipt numbers
* Offline queue capability with automatic retry

INVOICE/PAYMENT FEATURES
------------------------
* Payment-triggered eTIMS submission (NOT on invoice posting)
* Supports fully paid invoices only - partial payments wait
* Credit note/refund handling with reason codes
* Batch payment registration support
* Clear audit trail for compliance

REFUND REASON CODES (per OSCU Spec Section 4.16)
------------------------------------------------
* 01 - Return
* 02 - Incorrect Information
* 03 - Omission
* 04 - Cancellation
* 05 - Other

This module requires the base Kenya eTIMS module (l10n_ke_etims).
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': [
        'point_of_sale',
        'l10n_ke_etims',
    ],
    'data': [
        # No new models, only extending existing ones - no security rules needed
        'views/account_move_views.xml',
        'views/pos_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'l10n_ke_etims_pos/static/src/js/pos_etims.js',
            'l10n_ke_etims_pos/static/src/xml/pos_etims.xml',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
