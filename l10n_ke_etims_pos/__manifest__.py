# -*- coding: utf-8 -*-
{
    'name': 'Kenya - eTIMS POS Integration',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'KRA eTIMS integration for Point of Sale',
    'description': """
Kenya eTIMS POS Integration
===========================

This module extends the Point of Sale for Kenya Revenue Authority's
electronic Tax Invoice Management System (eTIMS) compliance.

Features:
---------
* Real-time POS order submission to eTIMS at payment
* Batch submission at session close for any missed orders
* POS return/refund handling with reason codes
* Session-level eTIMS submission tracking
* eTIMS receipt printing with SCU and receipt numbers
* Offline queue capability

Key Integration Points:
-----------------------
* POS order submission when payment is completed
* Automatic retry for failed submissions
* Session close ensures all orders are submitted
* Payment registration triggers invoice submission

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
