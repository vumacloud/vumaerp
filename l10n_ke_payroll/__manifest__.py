# -*- coding: utf-8 -*-
{
    'name': 'Kenya - Payroll',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Kenya Payroll with PAYE, NHIF, NSSF, and Housing Levy',
    'description': """
Kenya Payroll Localization
==========================

This module extends Odoo Payroll with Kenya-specific statutory deductions and contributions.

Statutory Deductions:
--------------------
* **PAYE (Pay As You Earn)**: Income tax calculated using KRA tax bands with personal relief
* **NHIF (National Hospital Insurance Fund)**: Health insurance based on salary bands
* **NSSF (National Social Security Fund)**: Tier I and Tier II contributions
* **Housing Levy**: 1.5% Affordable Housing Levy

Features:
---------
* Pre-configured salary structure for Kenya
* Automatic tax band calculations
* Personal relief of KES 2,400/month
* Insurance relief for NHIF contributions
* Employee and employer NSSF contributions
* Payslip reports with Kenyan format
* P9 Tax Certificate generation

Tax Bands (Monthly - 2024):
--------------------------
* 0 - 24,000: 10%
* 24,001 - 32,333: 25%
* 32,334 - 500,000: 30%
* 500,001 - 800,000: 32.5%
* Above 800,000: 35%

NHIF Rates (2024):
-----------------
Salary-based bands from KES 150 to KES 1,700/month

NSSF (2024):
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
        'data/hr_salary_rule_data.xml',
        'data/nhif_rates_data.xml',
        'data/paye_tax_bands_data.xml',
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
