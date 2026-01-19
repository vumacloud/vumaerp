# -*- coding: utf-8 -*-
{
    'name': 'Kenya - Payroll',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Kenya Payroll with PAYE, SHIF (SHA), NSSF, and Housing Levy',
    'description': """
Kenya Payroll Localization
==========================

This module extends Odoo Payroll with Kenya-specific statutory deductions and contributions.

Statutory Deductions (2025):
---------------------------
* **PAYE (Pay As You Earn)**: Income tax calculated using KRA tax bands with personal relief
* **SHIF (Social Health Insurance Fund)**: 2.75% of gross salary (min KES 300) - replaced NHIF Oct 2024
* **NSSF (National Social Security Fund)**: Tier I and Tier II contributions
* **Housing Levy**: 1.5% Affordable Housing Levy

Features:
---------
* Pre-configured salary structure for Kenya
* Automatic tax band calculations
* Personal relief of KES 2,400/month
* Insurance relief for SHIF contributions (15%, max KES 5,000)
* Employee and employer NSSF contributions
* Payslip reports with Kenyan format

Tax Bands (Monthly - 2025):
--------------------------
* 0 - 24,000: 10%
* 24,001 - 32,333: 25%
* 32,334 - 500,000: 30%
* 500,001 - 800,000: 32.5%
* Above 800,000: 35%

SHIF/SHA (Effective Oct 2024):
-----------------------------
* 2.75% of gross salary
* Minimum contribution: KES 300/month
* No maximum cap (unlike old NHIF bands)
* Tax deductible

NSSF (2025):
-----------
* Tier I: 6% on first KES 7,000 (max KES 420)
* Tier II: 6% on next KES 29,000 (max KES 1,740)
* Total max: KES 2,160/month (employee + employer)

Housing Levy:
------------
* 1.5% of gross salary (employee)
* 1.5% of gross salary (employer)
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'Other proprietary',
    'depends': [
        'hr',
        'om_hr_payroll',
        'om_hr_payroll_account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_salary_rule_category_data.xml',
        'data/hr_payroll_structure_data.xml',
        'data/paye_tax_bands_data.xml',
        'data/hr_salary_rule_data.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
        'views/kenya_payroll_config_views.xml',
        'views/kenya_payroll_menu.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
