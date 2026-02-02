# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # Nigeria statutory computed fields
    ng_gross_salary = fields.Monetary(
        string='Gross Salary',
        compute='_compute_ng_statutory',
        currency_field='currency_id',
    )
    ng_cra = fields.Monetary(
        string='CRA (Relief)',
        compute='_compute_ng_statutory',
        currency_field='currency_id',
    )
    ng_taxable_income = fields.Monetary(
        string='Taxable Income',
        compute='_compute_ng_statutory',
        currency_field='currency_id',
    )
    ng_paye = fields.Monetary(
        string='PAYE',
        compute='_compute_ng_statutory',
        currency_field='currency_id',
    )
    ng_pension_employee = fields.Monetary(
        string='Pension (Employee)',
        compute='_compute_ng_statutory',
        currency_field='currency_id',
    )
    ng_pension_employer = fields.Monetary(
        string='Pension (Employer)',
        compute='_compute_ng_statutory',
        currency_field='currency_id',
    )
    ng_nhf = fields.Monetary(
        string='NHF',
        compute='_compute_ng_statutory',
        currency_field='currency_id',
    )
    ng_nhis_employee = fields.Monetary(
        string='NHIS (Employee)',
        compute='_compute_ng_statutory',
        currency_field='currency_id',
    )

    @api.depends('contract_id', 'line_ids')
    def _compute_ng_statutory(self):
        PAYEBand = self.env['nigeria.paye.tax.band']
        StatutoryConfig = self.env['nigeria.statutory.config']

        for payslip in self:
            contract = payslip.contract_id

            if not contract:
                payslip.ng_gross_salary = 0
                payslip.ng_cra = 0
                payslip.ng_taxable_income = 0
                payslip.ng_paye = 0
                payslip.ng_pension_employee = 0
                payslip.ng_pension_employer = 0
                payslip.ng_nhf = 0
                payslip.ng_nhis_employee = 0
                continue

            # Get monthly and annual gross
            monthly_gross = contract.ng_gross_salary or contract.wage
            annual_gross = monthly_gross * 12

            # Get config
            config = StatutoryConfig.get_config(payslip.company_id)

            # Calculate pension (on basic salary)
            basic = contract.wage
            pension_ee_rate = contract.ng_pension_employee_rate or 8.0
            pension_er_rate = contract.ng_pension_employer_rate or 10.0

            pension_employee = basic * (pension_ee_rate / 100)
            pension_employer = basic * (pension_er_rate / 100)

            # Calculate NHF (on basic)
            nhf = 0
            if config:
                nhf = config.calculate_nhf(basic)
            else:
                nhf = basic * 0.025

            # Calculate NHIS
            nhis_employee = 0
            if contract.ng_nhis_enrolled and config:
                nhis_employee = config.calculate_nhis_employee(basic)

            # Calculate CRA (annual)
            if config:
                annual_cra = config.calculate_cra(annual_gross)
            else:
                # Default CRA calculation
                gross_threshold = annual_gross * 0.01
                base_cra = max(200000, gross_threshold)
                annual_cra = base_cra + (annual_gross * 0.20)

            monthly_cra = annual_cra / 12

            # Taxable income (annual) = Gross - CRA - Pension (Employee) - NHF
            annual_pension_ee = pension_employee * 12
            annual_nhf = nhf * 12
            annual_taxable = annual_gross - annual_cra - annual_pension_ee - annual_nhf

            # Calculate PAYE (monthly)
            monthly_paye = PAYEBand.calculate_monthly_paye(
                annual_taxable / 12,
                payslip.company_id
            )

            payslip.ng_gross_salary = monthly_gross
            payslip.ng_cra = monthly_cra
            payslip.ng_taxable_income = annual_taxable / 12
            payslip.ng_paye = monthly_paye
            payslip.ng_pension_employee = pension_employee
            payslip.ng_pension_employer = pension_employer
            payslip.ng_nhf = nhf
            payslip.ng_nhis_employee = nhis_employee
