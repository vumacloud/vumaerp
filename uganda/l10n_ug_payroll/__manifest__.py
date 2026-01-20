# -*- coding: utf-8 -*-
{
    'name': 'Uganda - Payroll',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Uganda Payroll with PAYE, NSSF, and LST',
    'description': """
Uganda Payroll Localization
===========================

This module extends Odoo Payroll with Uganda-specific statutory deductions.

Statutory Deductions (2025):
---------------------------
* **PAYE (Pay As You Earn)**: Progressive tax (10%-40%)
* **NSSF**: 5% employee + 10% employer
* **LST (Local Service Tax)**: Based on income and local government

PAYE Tax Bands (Monthly - Resident):
-----------------------------------
* 0 - 235,000: 0%
* 235,001 - 335,000: 10%
* 335,001 - 410,000: 20%
* 410,001 - 10,000,000: 30%
* Above 10,000,000: 40% (30% + 10% surcharge)

NSSF (2025):
-----------
* Employee: 5% of gross salary
* Employer: 10% of gross salary
* Total: 15%

Local Service Tax (LST):
-----------------------
* Varies by local government
* Deducted in 4 installments (July-October)
* Based on annual income bands
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'Other proprietary',
    'depends': [
        'hr',
        'om_hr_payroll',
        'om_hr_payroll_account',
        'l10n_ug',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_salary_rule_category_data.xml',
        'data/hr_payroll_structure_data.xml',
        'data/paye_tax_bands_data.xml',
        'data/hr_salary_rule_data.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
        'views/uganda_payroll_config_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
