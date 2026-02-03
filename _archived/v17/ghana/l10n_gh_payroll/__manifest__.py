# -*- coding: utf-8 -*-
{
    'name': 'Ghana - Payroll',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Ghana Payroll with PAYE, SSNIT, and Tier 2 Pension',
    'description': """
Ghana Payroll Localization for Odoo 17
======================================

Complete payroll solution for Ghana including:

**PAYE (Pay As You Earn)**
- Progressive tax bands
- Tax relief for residents

**SSNIT (Social Security)**
- Employee: 5.5% of basic salary
- Employer: 13% of basic salary
- Total: 18.5%

**Tier 2 Pension**
- Employee: 5% of basic salary
- Managed by approved trustees

**Tier 3 (Voluntary)**
- Optional provident fund contributions

**Features**
- Automatic statutory deduction calculations
- PAYE tax bands management
- Monthly GRA reports
- SSNIT contribution tracking
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'hr_contract',
        'l10n_gh',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_salary_rule_category_data.xml',
        'data/hr_payroll_structure_data.xml',
        'data/paye_tax_bands_data.xml',
        'views/hr_contract_views.xml',
        'views/ghana_statutory_config_views.xml',
        'views/paye_tax_band_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
