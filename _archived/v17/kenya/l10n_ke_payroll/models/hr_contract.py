# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # Kenya Allowances
    ke_house_allowance = fields.Monetary(string='House Allowance')
    ke_transport_allowance = fields.Monetary(string='Transport Allowance')
    ke_medical_allowance = fields.Monetary(string='Medical Allowance')
    ke_other_allowances = fields.Monetary(string='Other Allowances')

    # Pension
    ke_private_pension = fields.Monetary(
        string='Private Pension Contribution',
        help='Monthly contribution to private pension scheme (tax deductible up to KES 20,000)'
    )
    ke_pension_opt_out = fields.Boolean(
        string='NSSF Opt Out',
        help='Employee has opted out of NSSF (e.g., expatriates)'
    )

    # Computed fields
    ke_gross_salary = fields.Monetary(
        string='Gross Salary',
        compute='_compute_ke_gross_salary',
        store=True
    )

    @api.depends('wage', 'ke_house_allowance', 'ke_transport_allowance',
                 'ke_medical_allowance', 'ke_other_allowances')
    def _compute_ke_gross_salary(self):
        for contract in self:
            contract.ke_gross_salary = (
                contract.wage +
                (contract.ke_house_allowance or 0) +
                (contract.ke_transport_allowance or 0) +
                (contract.ke_medical_allowance or 0) +
                (contract.ke_other_allowances or 0)
            )
