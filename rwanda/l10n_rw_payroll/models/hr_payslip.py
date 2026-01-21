# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # Rwanda Tax Summary
    rw_gross_income = fields.Monetary(
        string='Gross Taxable Income',
        compute='_compute_rw_tax_summary',
        currency_field='currency_id'
    )
    rw_paye_amount = fields.Monetary(
        string='PAYE Amount',
        compute='_compute_rw_tax_summary',
        currency_field='currency_id'
    )
    rw_rssb_employee = fields.Monetary(
        string='RSSB (Employee)',
        compute='_compute_rw_tax_summary',
        currency_field='currency_id'
    )
    rw_rssb_employer = fields.Monetary(
        string='RSSB (Employer)',
        compute='_compute_rw_tax_summary',
        currency_field='currency_id'
    )

    @api.depends('line_ids')
    def _compute_rw_tax_summary(self):
        for payslip in self:
            gross = 0
            paye = 0
            rssb_ee = 0
            rssb_er = 0
            for line in payslip.line_ids:
                if line.code == 'GROSS':
                    gross = line.total
                elif line.code == 'PAYE':
                    paye = abs(line.total)
                elif line.code == 'RSSB_EE':
                    rssb_ee = abs(line.total)
                elif line.code == 'RSSB_ER':
                    rssb_er = abs(line.total)
            payslip.rw_gross_income = gross
            payslip.rw_paye_amount = paye
            payslip.rw_rssb_employee = rssb_ee
            payslip.rw_rssb_employer = rssb_er

    def compute_rw_paye(self, gross_income):
        """
        Compute Rwanda PAYE based on monthly income
        Rates (2024):
        - 0% for income up to RWF 30,000
        - 20% for income RWF 30,001 - 100,000
        - 30% for income above RWF 100,000
        """
        if gross_income <= 30000:
            return 0
        elif gross_income <= 100000:
            return (gross_income - 30000) * 0.20
        else:
            # First bracket: 0
            # Second bracket: (100000 - 30000) * 0.20 = 14,000
            # Third bracket: (gross - 100000) * 0.30
            return 14000 + (gross_income - 100000) * 0.30

    def compute_rw_rssb_employee(self, gross_income):
        """Employee RSSB Pension contribution: 3%"""
        return gross_income * 0.03

    def compute_rw_rssb_employer(self, gross_income):
        """
        Employer RSSB contributions:
        - Pension: 3%
        - Maternity: 0.3%
        - Occupational Hazards: 2%
        Total: 5.3%
        """
        return gross_income * 0.053
