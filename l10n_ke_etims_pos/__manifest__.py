# -*- coding: utf-8 -*-
{
    'name': 'Kenya - eTIMS POS Integration',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'KRA eTIMS integration for Point of Sale',
    'description': """
Kenya eTIMS POS & Payment Integration
=====================================

This module extends Point of Sale and Accounting for Kenya Revenue Authority's
electronic Tax Invoice Management System (eTIMS) compliance.

**CRITICAL COMPLIANCE FEATURE**: Submits to eTIMS only when payment is received,
not when invoice is posted. This aligns with KRA regulations and KPMG advisory
that income in eTIMS must represent actual sales transactions.

POS Features:
-------------
* Real-time POS order submission to eTIMS at payment completion
* Batch submission at session close for any missed orders
* POS return/refund handling with KRA reason codes
* Session-level eTIMS submission tracking (submitted/pending/failed stats)
* eTIMS receipt printing with SCU and receipt numbers
* Offline queue capability with automatic retry

Invoice/Payment Features:
-------------------------
* Payment-triggered eTIMS submission (NOT on invoice posting)
* Supports fully paid invoices only - partial payments wait
* Credit note/refund handling with reason codes
* Batch payment registration support
* Clear audit trail for compliance

Refund Reason Codes (per KRA):
------------------------------
* 01 - Damage/Defect
* 02 - Change of Mind
* 03 - Wrong Item Delivered
* 04 - Late Delivery
* 05 - Duplicate Order
* 06 - Price Dispute
* 07 - Quantity Dispute
* 08 - Quality Issues
* 09 - Order Cancellation
* 10 - Other

This module requires the base Kenya eTIMS module (l10n_ke_etims).
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'Other proprietary',
    'depends': [
        'point_of_sale',
        'l10n_ke_etims',
    ],
    'data': [
        'security/ir.model.access.csv',
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
