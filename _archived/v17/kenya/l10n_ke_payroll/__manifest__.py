# -*- coding: utf-8 -*-
{
    'name': 'Kenya - Payroll',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Kenya Payroll with PAYE, NSSF, SHIF, and Housing Levy',
    'description': """
Kenya Payroll Localization for Odoo 17
======================================

Complete payroll solution for Kenya including:

**PAYE (Pay As You Earn)**
- Progressive tax bands (10% - 35%)
- Personal relief (KES 2,400/month)
- Insurance relief (15% of SHIF, max KES 5,000/month)

**NSSF (National Social Security Fund)**
- Tier I: 6% of KES 7,000 (KES 420)
- Tier II: 6% of (Pensionable - 7,000), max KES 1,080
- Total max: KES 1,500/month each for employee and employer

**SHIF (Social Health Insurance Fund)**
- 2.75% of gross salary
- Replaced NHIF effective October 2024

**Housing Levy (Affordable Housing)**
- 1.5% of gross salary (employee)
- 1.5% of gross salary (employer)

**Features**
- Automatic statutory deduction calculations
- PAYE tax bands management
- Monthly P9 reports
- Integration with KRA systems
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'hr_contract',
        'l10n_ke',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_salary_rule_category_data.xml',
        'data/hr_payroll_structure_data.xml',
        'data/hr_salary_rule_data.xml',
        'data/paye_tax_bands_data.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
        'views/kenya_statutory_config_views.xml',
        'views/paye_tax_band_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
