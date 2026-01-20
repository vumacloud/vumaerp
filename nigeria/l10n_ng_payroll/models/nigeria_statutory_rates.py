# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class NigeriaPAYETaxBand(models.Model):
    _name = 'nigeria.paye.tax.band'
    _description = 'Nigeria PAYE Tax Band'
    _order = 'sequence, min_amount'

    name = fields.Char(string='Band Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    min_amount = fields.Float(string='Minimum Amount (NGN)', required=True)
    max_amount = fields.Float(string='Maximum Amount (NGN)', required=True)
    rate = fields.Float(string='Tax Rate (%)', required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    @api.model
    def calculate_paye(self, annual_taxable_income, company=None):
        """
        Calculate Nigeria PAYE using stepped/graduated method.
        Input is annual taxable income, returns annual tax.
        """
        if annual_taxable_income <= 0:
            return 0.0

        company = company or self.env.company
        bands = self.search([
            '|', ('company_id', '=', company.id), ('company_id', '=', False)
        ], order='sequence, min_amount')

        if not bands:
            return 0.0

        total_tax = 0.0
        remaining_income = annual_taxable_income

        for band in bands:
            if remaining_income <= 0:
                break

            band_width = band.max_amount - band.min_amount if band.max_amount > 0 else float('inf')

            if remaining_income > band_width:
                taxable_in_band = band_width
            else:
                taxable_in_band = remaining_income

            tax_in_band = taxable_in_band * (band.rate / 100)
            total_tax += tax_in_band
            remaining_income -= taxable_in_band

        return round(total_tax, 2)

    @api.model
    def calculate_monthly_paye(self, monthly_taxable_income, company=None):
        """Calculate monthly PAYE from monthly taxable income."""
        annual_income = monthly_taxable_income * 12
        annual_tax = self.calculate_paye(annual_income, company)
        return round(annual_tax / 12, 2)


class NigeriaStatutoryConfig(models.Model):
    _name = 'nigeria.statutory.config'
    _description = 'Nigeria Statutory Configuration'
    _rec_name = 'name'

    name = fields.Char(string='Configuration Name', required=True, default='Default')
    active = fields.Boolean(default=True)

    # Pension rates
    pension_employee_rate = fields.Float(
        string='Pension Employee Rate (%)',
        default=8.0,
        help='Minimum employee contribution rate for pension (default 8%)',
    )
    pension_employer_rate = fields.Float(
        string='Pension Employer Rate (%)',
        default=10.0,
        help='Minimum employer contribution rate for pension (default 10%)',
    )

    # NHF rate
    nhf_rate = fields.Float(
        string='NHF Rate (%)',
        default=2.5,
        help='National Housing Fund rate (default 2.5%)',
    )

    # NHIS rates
    nhis_employee_rate = fields.Float(
        string='NHIS Employee Rate (%)',
        default=1.75,
        help='Employee NHIS contribution rate',
    )
    nhis_employer_rate = fields.Float(
        string='NHIS Employer Rate (%)',
        default=3.25,
        help='Employer NHIS contribution rate',
    )

    # CRA (Consolidated Relief Allowance)
    cra_fixed = fields.Float(
        string='CRA Fixed Amount (NGN)',
        default=200000.0,
        help='Fixed CRA amount per annum',
    )
    cra_percentage = fields.Float(
        string='CRA Percentage (%)',
        default=20.0,
        help='CRA percentage of gross income',
    )
    cra_gross_threshold = fields.Float(
        string='CRA Gross Threshold (%)',
        default=1.0,
        help='CRA is higher of fixed amount or this % of gross',
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    @api.model
    def get_config(self, company=None):
        """Get active configuration for company."""
        company = company or self.env.company
        config = self.search([
            ('active', '=', True),
            '|', ('company_id', '=', company.id), ('company_id', '=', False)
        ], limit=1)
        return config

    def calculate_cra(self, annual_gross):
        """
        Calculate Consolidated Relief Allowance.
        CRA = Higher of (NGN 200,000 OR 1% of Gross) + 20% of Gross
        """
        self.ensure_one()
        gross_threshold = annual_gross * (self.cra_gross_threshold / 100)
        base_cra = max(self.cra_fixed, gross_threshold)
        percentage_cra = annual_gross * (self.cra_percentage / 100)
        return round(base_cra + percentage_cra, 2)

    def calculate_pension_employee(self, basic_salary):
        """Calculate pension employee contribution."""
        self.ensure_one()
        return round(basic_salary * (self.pension_employee_rate / 100), 2)

    def calculate_pension_employer(self, basic_salary):
        """Calculate pension employer contribution."""
        self.ensure_one()
        return round(basic_salary * (self.pension_employer_rate / 100), 2)

    def calculate_nhf(self, basic_salary):
        """Calculate National Housing Fund contribution."""
        self.ensure_one()
        return round(basic_salary * (self.nhf_rate / 100), 2)

    def calculate_nhis_employee(self, basic_salary):
        """Calculate NHIS employee contribution."""
        self.ensure_one()
        return round(basic_salary * (self.nhis_employee_rate / 100), 2)

    def calculate_nhis_employer(self, basic_salary):
        """Calculate NHIS employer contribution."""
        self.ensure_one()
        return round(basic_salary * (self.nhis_employer_rate / 100), 2)
