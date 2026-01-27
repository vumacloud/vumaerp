# -*- coding: utf-8 -*-
{
    'name': 'Rwanda - Payroll',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Rwanda Payroll with PAYE, RSSB, and CBHI',
    'description': """
Rwanda Payroll Localization
===========================

Complete payroll solution for Rwanda including:

**PAYE (Pay As You Earn)**
- 0% for income up to RWF 30,000
- 20% for income RWF 30,001 - 100,000
- 30% for income above RWF 100,000

**RSSB (Rwanda Social Security Board)**
- Pension: 3% employee + 3% employer (6% total)
- Maternity Leave: 0.3% employer
- Occupational Hazards: 2% employer

**CBHI (Community Based Health Insurance)**
- Mandatory health insurance contribution

**Features**
- Automatic tax calculations
- RSSB contribution management
- Monthly declaration reports
- Integration with RRA systems
    """,
    'author': 'VumaCloud',
    'website': 'https://vumacloud.com',
    'license': 'Other proprietary',
    'depends': [
        'hr',
        'om_hr_payroll',
        'om_hr_payroll_account',
        'l10n_rw',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_salary_rule_category_data.xml',
        'data/hr_salary_rule_data.xml',
        'data/hr_payroll_structure_data.xml',
        'views/hr_employee_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
