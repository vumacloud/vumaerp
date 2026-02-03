# -*- coding: utf-8 -*-
{
    'name': 'Ghana - E-VAT Integration',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Ghana Revenue Authority E-VAT Integration',
    'description': """
Ghana E-VAT Integration for Odoo 17
===================================

Integration with Ghana Revenue Authority's Electronic VAT (E-VAT) system.

**Features**
- Electronic invoice submission to GRA
- VAT return preparation
- Automatic tax calculation
- Invoice validation and verification
- Real-time submission status tracking

**VAT Rates**
- Standard Rate: 15% (12.5% VAT + 2.5% NHIL + COVID Levy)
- Flat Rate: 3%
- Zero Rated: 0%
- Exempt: N/A

**Compliance**
- TIN validation
- Invoice numbering requirements
- E-VAT filing deadlines
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'sale',
        'purchase',
        'l10n_gh',
    ],
    'data': [
        'security/evat_security.xml',
        'security/ir.model.access.csv',
        'views/evat_config_views.xml',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
