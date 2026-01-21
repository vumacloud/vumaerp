# -*- coding: utf-8 -*-
{
    'name': 'Rwanda - EBM Integration',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Electronic Billing Machine (EBM) integration for Rwanda',
    'description': """
Rwanda EBM Integration
======================

Integration with Rwanda Revenue Authority's Electronic Billing Machine system.

**Features:**
- EBM invoice submission to RRA
- Real-time invoice validation
- EBM receipt number tracking
- VAT compliance reporting
- Automatic tax calculations (18% VAT)

**Invoice Types:**
- Normal Sale (NS)
- Copy (CP)
- Training Invoice (TR)
- Proforma Invoice (PF)

**Requirements:**
- RRA-registered EBM device
- Valid EBM API credentials
- TIN registration with RRA

Compliant with RRA EBM requirements for VAT-registered businesses.
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'Other proprietary',
    'depends': [
        'account',
        'l10n_rw',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ebm_security.xml',
        'data/account_tax_data.xml',
        'views/res_company_views.xml',
        'views/account_move_views.xml',
        'views/ebm_config_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
