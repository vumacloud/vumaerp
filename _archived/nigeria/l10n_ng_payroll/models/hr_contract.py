# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # Nigeria-specific contract fields
    ng_tin = fields.Char(
        string='TIN',
        help='Federal Inland Revenue Service Tax Identification Number',
    )
    ng_pension_pin = fields.Char(
        string='Pension PIN',
        help='PenCom Retirement Savings Account (RSA) PIN',
    )
    ng_pfa_id = fields.Char(
        string='PFA ID',
        help='Pension Fund Administrator identifier',
    )
    ng_pfa_name = fields.Char(
        string='PFA Name',
        help='Name of Pension Fund Administrator',
    )
    ng_nhf_number = fields.Char(
        string='NHF Number',
        help='National Housing Fund registration number',
    )

    # Allowances (common in Nigeria)
    ng_transport_allowance = fields.Monetary(
        string='Transport Allowance',
        currency_field='currency_id',
        default=0.0,
    )
    ng_housing_allowance = fields.Monetary(
        string='Housing Allowance',
        currency_field='currency_id',
        default=0.0,
    )
    ng_meal_allowance = fields.Monetary(
        string='Meal/Feeding Allowance',
        currency_field='currency_id',
        default=0.0,
    )
    ng_utility_allowance = fields.Monetary(
        string='Utility Allowance',
        currency_field='currency_id',
        default=0.0,
    )
    ng_furniture_allowance = fields.Monetary(
        string='Furniture Allowance',
        currency_field='currency_id',
        default=0.0,
    )
    ng_leave_allowance = fields.Monetary(
        string='Leave Allowance',
        currency_field='currency_id',
        default=0.0,
    )
    ng_other_allowance = fields.Monetary(
        string='Other Allowance',
        currency_field='currency_id',
        default=0.0,
    )

    # Override pension rates if different from default
    ng_pension_employee_rate = fields.Float(
        string='Pension Employee (%)',
        default=8.0,
        help='Employee pension contribution rate (min 8%)',
    )
    ng_pension_employer_rate = fields.Float(
        string='Pension Employer (%)',
        default=10.0,
        help='Employer pension contribution rate (min 10%)',
    )

    # NHIS participation
    ng_nhis_enrolled = fields.Boolean(
        string='NHIS Enrolled',
        default=True,
        help='Employee enrolled in National Health Insurance Scheme',
    )

    # Computed gross salary
    ng_gross_salary = fields.Monetary(
        string='Gross Salary',
        compute='_compute_ng_gross_salary',
        store=True,
        currency_field='currency_id',
    )

    @api.depends('wage', 'ng_transport_allowance', 'ng_housing_allowance',
                 'ng_meal_allowance', 'ng_utility_allowance', 'ng_furniture_allowance',
                 'ng_leave_allowance', 'ng_other_allowance')
    def _compute_ng_gross_salary(self):
        for contract in self:
            contract.ng_gross_salary = (
                contract.wage +
                contract.ng_transport_allowance +
                contract.ng_housing_allowance +
                contract.ng_meal_allowance +
                contract.ng_utility_allowance +
                contract.ng_furniture_allowance +
                contract.ng_leave_allowance +
                contract.ng_other_allowance
            )
