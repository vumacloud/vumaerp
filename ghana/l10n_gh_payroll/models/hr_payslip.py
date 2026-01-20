# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # Ghana statutory computed fields
    gh_gross_salary = fields.Monetary(
        string='Gross Salary',
        compute='_compute_gh_statutory',
        currency_field='currency_id',
    )
    gh_taxable_income = fields.Monetary(
        string='Taxable Income',
        compute='_compute_gh_statutory',
        currency_field='currency_id',
    )
    gh_paye = fields.Monetary(
        string='PAYE',
        compute='_compute_gh_statutory',
        currency_field='currency_id',
    )
    gh_ssnit_employee = fields.Monetary(
        string='SSNIT (Employee)',
        compute='_compute_gh_statutory',
        currency_field='currency_id',
    )
    gh_ssnit_employer = fields.Monetary(
        string='SSNIT (Employer)',
        compute='_compute_gh_statutory',
        currency_field='currency_id',
    )
    gh_tier2 = fields.Monetary(
        string='Tier 2 Pension',
        compute='_compute_gh_statutory',
        currency_field='currency_id',
    )

    @api.depends('contract_id', 'line_ids')
    def _compute_gh_statutory(self):
        PAYEBand = self.env['ghana.paye.tax.band']
        StatutoryConfig = self.env['ghana.statutory.config']

        for payslip in self:
            contract = payslip.contract_id

            if not contract:
                payslip.gh_gross_salary = 0
                payslip.gh_taxable_income = 0
                payslip.gh_paye = 0
                payslip.gh_ssnit_employee = 0
                payslip.gh_ssnit_employer = 0
                payslip.gh_tier2 = 0
                continue

            # Get gross salary from contract
            gross = contract.gh_gross_salary or contract.wage

            # Get config
            config = StatutoryConfig.get_config(payslip.company_id)

            # Calculate SSNIT and Tier 2 (based on basic salary)
            basic = contract.wage
            ssnit_employee = 0
            ssnit_employer = 0
            tier2 = 0

            if config:
                ssnit_employee = config.calculate_ssnit_employee(basic)
                ssnit_employer = config.calculate_ssnit_employer(basic)
                tier2 = config.calculate_tier2(basic)
            else:
                # Default rates
                ssnit_employee = basic * 0.055
                ssnit_employer = basic * 0.08
                tier2 = basic * 0.05

            # Taxable income = Gross - SSNIT Employee - Tier 2 Employee portion
            # In Ghana, employee SSNIT contribution is tax deductible
            taxable_income = gross - ssnit_employee

            # Calculate PAYE
            paye = PAYEBand.calculate_paye(taxable_income, payslip.company_id)

            payslip.gh_gross_salary = gross
            payslip.gh_taxable_income = taxable_income
            payslip.gh_paye = paye
            payslip.gh_ssnit_employee = ssnit_employee
            payslip.gh_ssnit_employer = ssnit_employer
            payslip.gh_tier2 = tier2
