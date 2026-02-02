# -*- coding: utf-8 -*-
{
    'name': 'Nigeria - Payroll',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Nigeria Payroll with PAYE, Pension, NHF, and NHIS',
    'description': """
Nigeria Payroll Localization
============================

This module extends Odoo Payroll with Nigeria-specific statutory deductions.

Statutory Deductions (2025):
---------------------------
* **PAYE**: Progressive income tax (7%-24%)
* **Pension**: 8% employee + 10% employer (minimum)
* **NHF**: 2.5% (National Housing Fund)
* **NHIS**: 1.75% employee + 3.25% employer (formal sector)

PAYE Tax Bands (Annual - NGN):
-----------------------------
* 0 - 300,000: 7%
* 300,001 - 600,000: 11%
* 600,001 - 1,100,000: 15%
* 1,100,001 - 1,600,000: 19%
* 1,600,001 - 3,200,000: 21%
* Above 3,200,000: 24%

Consolidated Relief Allowance (CRA):
-----------------------------------
* Higher of NGN 200,000 or 1% of gross income
* Plus 20% of gross income

Pension (PFA - Pension Fund Administrator):
------------------------------------------
* Employee: 8% minimum
* Employer: 10% minimum
* Total: 18% minimum (can be higher)

NHF (National Housing Fund):
---------------------------
* 2.5% of basic salary
* Mandatory for employees earning above minimum wage
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'Other proprietary',
    'depends': [
        'hr',
        'om_hr_payroll',
        'om_hr_payroll_account',
        'l10n_ng',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_salary_rule_category_data.xml',
        'data/hr_payroll_structure_data.xml',
        'data/paye_tax_bands_data.xml',
        'data/hr_salary_rule_data.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
        'views/nigeria_payroll_config_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
