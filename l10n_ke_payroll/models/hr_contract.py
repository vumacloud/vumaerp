# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # Kenya-specific fields
    ke_pension_opt_out = fields.Boolean(
        string='Opted Out of NSSF',
        default=False,
        help='Employee has opted out of NSSF contributions (for employees with private pension schemes)',
    )
    ke_private_pension = fields.Float(
        string='Private Pension Contribution',
        default=0.0,
        help='Monthly contribution to registered private pension scheme',
    )
    ke_mortgage_interest = fields.Float(
        string='Mortgage Interest',
        default=0.0,
        help='Monthly mortgage interest for owner-occupied property (max KES 25,000)',
    )
    ke_disability_exemption = fields.Boolean(
        string='Disability Exemption',
        default=False,
        help='Employee qualifies for disability exemption (first KES 150,000/month exempt)',
    )
    ke_nhif_number = fields.Char(
        string='NHIF Number',
        help='Employee NHIF membership number',
    )
    ke_nssf_number = fields.Char(
        string='NSSF Number',
        help='Employee NSSF membership number',
    )
    ke_kra_pin = fields.Char(
        string='KRA PIN',
        related='employee_id.identification_id',
        readonly=True,
        help='Employee KRA PIN for tax purposes',
    )

    # Allowances (Kenya specific)
    ke_house_allowance = fields.Float(
        string='House Allowance',
        default=0.0,
        help='Monthly housing allowance',
    )
    ke_transport_allowance = fields.Float(
        string='Transport Allowance',
        default=0.0,
        help='Monthly transport allowance',
    )
    ke_medical_allowance = fields.Float(
        string='Medical Allowance',
        default=0.0,
        help='Monthly medical allowance',
    )
    ke_other_allowances = fields.Float(
        string='Other Taxable Allowances',
        default=0.0,
        help='Other taxable allowances',
    )

    # Non-cash benefits
    ke_company_car_value = fields.Float(
        string='Company Car Benefit',
        default=0.0,
        help='Monthly value of company car benefit',
    )
    ke_housing_benefit = fields.Float(
        string='Housing Benefit',
        default=0.0,
        help='Monthly value of company-provided housing',
    )

    @api.depends('wage', 'ke_house_allowance', 'ke_transport_allowance',
                 'ke_medical_allowance', 'ke_other_allowances')
    def _compute_gross_salary(self):
        """Compute gross salary including allowances."""
        for contract in self:
            contract.ke_gross_salary = (
                contract.wage +
                contract.ke_house_allowance +
                contract.ke_transport_allowance +
                contract.ke_medical_allowance +
                contract.ke_other_allowances
            )

    ke_gross_salary = fields.Float(
        string='Gross Salary',
        compute='_compute_gross_salary',
        store=True,
        help='Total gross salary including all allowances',
    )
