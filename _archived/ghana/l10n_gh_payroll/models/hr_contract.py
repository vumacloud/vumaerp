# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # Ghana-specific contract fields
    gh_tin = fields.Char(
        string='TIN',
        help='Ghana Revenue Authority Taxpayer Identification Number',
    )
    gh_ssnit_number = fields.Char(
        string='SSNIT Number',
        help='Social Security and National Insurance Trust number',
    )
    gh_tier2_provider = fields.Char(
        string='Tier 2 Provider',
        help='Name of the Tier 2 pension trustee/provider',
    )
    gh_tier3_provider = fields.Char(
        string='Tier 3 Provider',
        help='Name of the Tier 3 voluntary pension provider',
    )

    # Allowances
    gh_transport_allowance = fields.Monetary(
        string='Transport Allowance',
        currency_field='currency_id',
        default=0.0,
    )
    gh_housing_allowance = fields.Monetary(
        string='Housing Allowance',
        currency_field='currency_id',
        default=0.0,
    )
    gh_risk_allowance = fields.Monetary(
        string='Risk Allowance',
        currency_field='currency_id',
        default=0.0,
    )
    gh_responsibility_allowance = fields.Monetary(
        string='Responsibility Allowance',
        currency_field='currency_id',
        default=0.0,
    )
    gh_other_allowance = fields.Monetary(
        string='Other Allowance',
        currency_field='currency_id',
        default=0.0,
    )

    # Tier 3 voluntary contribution
    gh_tier3_employee = fields.Float(
        string='Tier 3 Employee (%)',
        default=0.0,
        help='Voluntary Tier 3 employee contribution rate',
    )
    gh_tier3_employer = fields.Float(
        string='Tier 3 Employer (%)',
        default=0.0,
        help='Voluntary Tier 3 employer contribution rate',
    )

    # Computed gross salary
    gh_gross_salary = fields.Monetary(
        string='Gross Salary',
        compute='_compute_gh_gross_salary',
        store=True,
        currency_field='currency_id',
    )

    @api.depends('wage', 'gh_transport_allowance', 'gh_housing_allowance',
                 'gh_risk_allowance', 'gh_responsibility_allowance', 'gh_other_allowance')
    def _compute_gh_gross_salary(self):
        for contract in self:
            contract.gh_gross_salary = (
                contract.wage +
                contract.gh_transport_allowance +
                contract.gh_housing_allowance +
                contract.gh_risk_allowance +
                contract.gh_responsibility_allowance +
                contract.gh_other_allowance
            )
