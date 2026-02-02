# -*- coding: utf-8 -*-
{
    'name': 'Odoo HR Payroll Community',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Manage employee payroll',
    'description': """
Odoo HR Payroll Community Edition
=================================

This module provides payroll management functionality including:
- Payslip generation and processing
- Salary rules and structures
- Contribution registers
- Payroll reports

Based on OCA hr_payroll module, adapted for Odoo 17.
    """,
    'author': 'VumaCloud, Odoo Community Association (OCA)',
    'website': 'https://vumacloud.com',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'hr_contract',
        'account',
    ],
    'data': [
        'security/hr_payroll_security.xml',
        'security/ir.model.access.csv',
        'data/hr_payroll_sequence.xml',
        'data/hr_payroll_category_data.xml',
        'views/hr_payroll_structure_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_payroll_menu.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
