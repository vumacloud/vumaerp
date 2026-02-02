# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # Uganda-specific allowances
    ug_house_allowance = fields.Float(string='House Allowance')
    ug_transport_allowance = fields.Float(string='Transport Allowance')
    ug_medical_allowance = fields.Float(string='Medical Allowance')
    ug_lunch_allowance = fields.Float(string='Lunch Allowance')
    ug_other_allowances = fields.Float(string='Other Allowances')

    # Non-cash benefits (taxable)
    ug_housing_benefit = fields.Float(string='Housing Benefit (Non-Cash)')
    ug_car_benefit = fields.Float(string='Car Benefit (Non-Cash)')
    ug_other_benefits = fields.Float(string='Other Benefits (Non-Cash)')

    # Tax settings
    ug_resident_status = fields.Selection([
        ('resident', 'Resident'),
        ('non_resident', 'Non-Resident'),
    ], string='Resident Status', default='resident')

    ug_tin = fields.Char(string='TIN', size=14, help='Taxpayer Identification Number')
    ug_nssf_number = fields.Char(string='NSSF Number')

    # Local Service Tax
    ug_local_government = fields.Char(string='Local Government', default='Kampala')
    ug_lst_exempt = fields.Boolean(string='LST Exempt', default=False)

    # Deduction opt-outs
    ug_nssf_opt_out = fields.Boolean(string='NSSF Opt-Out', default=False,
                                      help='Check if employee is exempt from NSSF')

    @api.depends('wage', 'ug_house_allowance', 'ug_transport_allowance',
                 'ug_medical_allowance', 'ug_lunch_allowance', 'ug_other_allowances',
                 'ug_housing_benefit', 'ug_car_benefit', 'ug_other_benefits')
    def _compute_ug_gross_salary(self):
        for contract in self:
            contract.ug_gross_salary = (
                contract.wage +
                (contract.ug_house_allowance or 0) +
                (contract.ug_transport_allowance or 0) +
                (contract.ug_medical_allowance or 0) +
                (contract.ug_lunch_allowance or 0) +
                (contract.ug_other_allowances or 0) +
                (contract.ug_housing_benefit or 0) +
                (contract.ug_car_benefit or 0) +
                (contract.ug_other_benefits or 0)
            )

    ug_gross_salary = fields.Float(
        string='Gross Salary',
        compute='_compute_ug_gross_salary',
        store=True,
    )
