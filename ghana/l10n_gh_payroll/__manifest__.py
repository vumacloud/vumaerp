# -*- coding: utf-8 -*-
{
    'name': 'Ghana - Payroll',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Ghana Payroll with PAYE, SSNIT, and Tier 2/3 Pension',
    'description': """
Ghana Payroll Localization
==========================

This module extends Odoo Payroll with Ghana-specific statutory deductions.

Statutory Deductions (2025):
---------------------------
* **PAYE**: Progressive income tax (0%-35%)
* **SSNIT (Tier 1)**: 5.5% employee + 13% employer
* **Tier 2 Pension**: 5% (managed by trustees)
* **Tier 3 (Voluntary)**: Up to 16.5%

PAYE Tax Bands (Monthly - GHS):
------------------------------
* 0 - 490: 0%
* 491 - 600: 5%
* 601 - 730: 10%
* 731 - 3,896: 17.5%
* 3,897 - 20,000: 25%
* 20,001 - 50,000: 30%
* Above 50,000: 35%

Pension Structure:
-----------------
* **Tier 1 (SSNIT)**: Mandatory - 13.5% (5.5% employee + 8% employer to SSNIT)
* **Tier 2**: Mandatory - 5% employer contribution (managed by trustees)
* **Tier 3**: Voluntary provident fund

Note: Employer contributes 13% total, split between SSNIT (8%) and Tier 2 (5%)
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'Other proprietary',
    'depends': [
        'hr',
        'om_hr_payroll',
        'om_hr_payroll_account',
        'l10n_gh',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_salary_rule_category_data.xml',
        'data/hr_payroll_structure_data.xml',
        'data/paye_tax_bands_data.xml',
        'data/hr_salary_rule_data.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
        'views/ghana_payroll_config_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
