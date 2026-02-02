# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # Ghana Allowances
    gh_housing_allowance = fields.Monetary(string='Housing Allowance')
    gh_transport_allowance = fields.Monetary(string='Transport Allowance')
    gh_risk_allowance = fields.Monetary(string='Risk Allowance')
    gh_other_allowances = fields.Monetary(string='Other Allowances')

    # Pension
    gh_tier3_contribution = fields.Monetary(
        string='Tier 3 Contribution',
        help='Voluntary provident fund contribution'
    )
    gh_ssnit_opt_out = fields.Boolean(
        string='SSNIT Opt Out',
        help='Employee has opted out of SSNIT (e.g., expatriates)'
    )

    # Tax
    gh_tax_relief = fields.Monetary(
        string='Additional Tax Relief',
        help='Additional tax relief claims'
    )

    # Computed fields
    gh_gross_salary = fields.Monetary(
        string='Gross Salary',
        compute='_compute_gh_gross_salary',
        store=True
    )

    @api.depends('wage', 'gh_housing_allowance', 'gh_transport_allowance',
                 'gh_risk_allowance', 'gh_other_allowances')
    def _compute_gh_gross_salary(self):
        for contract in self:
            contract.gh_gross_salary = (
                contract.wage +
                (contract.gh_housing_allowance or 0) +
                (contract.gh_transport_allowance or 0) +
                (contract.gh_risk_allowance or 0) +
                (contract.gh_other_allowances or 0)
            )
