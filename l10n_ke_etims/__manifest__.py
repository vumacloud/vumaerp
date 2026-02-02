# -*- coding: utf-8 -*-
{
    'name': 'Kenya eTIMS Integration',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'KRA eTIMS invoice submission for Kenya',
    'description': """
Send invoices to Kenya Revenue Authority eTIMS system.

Features:
- Submit sales invoices to KRA eTIMS
- Get SCU (Signed Code Unit) receipt numbers
- Track submission status on invoices
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/etims_config_views.xml',
        'views/account_move_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
}
