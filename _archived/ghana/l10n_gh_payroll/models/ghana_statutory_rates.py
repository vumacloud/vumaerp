# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class GhanaPAYETaxBand(models.Model):
    _name = 'ghana.paye.tax.band'
    _description = 'Ghana PAYE Tax Band'
    _order = 'sequence, min_amount'

    name = fields.Char(string='Band Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    min_amount = fields.Float(string='Minimum Amount (GHS)', required=True)
    max_amount = fields.Float(string='Maximum Amount (GHS)', required=True)
    rate = fields.Float(string='Tax Rate (%)', required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    @api.model
    def calculate_paye(self, taxable_income, company=None):
        """
        Calculate Ghana PAYE using cumulative/graduated method.
        Returns the tax amount.
        """
        if taxable_income <= 0:
            return 0.0

        company = company or self.env.company
        bands = self.search([
            '|', ('company_id', '=', company.id), ('company_id', '=', False)
        ], order='sequence, min_amount')

        if not bands:
            return 0.0

        total_tax = 0.0
        remaining_income = taxable_income

        for band in bands:
            if remaining_income <= 0:
                break

            band_min = band.min_amount
            band_max = band.max_amount
            band_width = band_max - band_min if band_max > 0 else float('inf')

            if remaining_income > band_width:
                taxable_in_band = band_width
            else:
                taxable_in_band = remaining_income

            tax_in_band = taxable_in_band * (band.rate / 100)
            total_tax += tax_in_band
            remaining_income -= taxable_in_band

        return round(total_tax, 2)


class GhanaStatutoryConfig(models.Model):
    _name = 'ghana.statutory.config'
    _description = 'Ghana Statutory Configuration'
    _rec_name = 'name'

    name = fields.Char(string='Configuration Name', required=True, default='Default')
    active = fields.Boolean(default=True)

    # SSNIT (Tier 1) rates
    ssnit_employee_rate = fields.Float(
        string='SSNIT Employee Rate (%)',
        default=5.5,
        help='Employee contribution rate for SSNIT Tier 1 (default 5.5%)',
    )
    ssnit_employer_rate = fields.Float(
        string='SSNIT Employer Rate (%)',
        default=13.0,
        help='Total employer contribution rate (13% split between SSNIT and Tier 2)',
    )

    # Tier 2 rates (from employer contribution)
    tier2_rate = fields.Float(
        string='Tier 2 Rate (%)',
        default=5.0,
        help='Tier 2 pension rate from employer contribution (default 5%)',
    )

    # Computed SSNIT employer portion
    ssnit_employer_portion = fields.Float(
        string='SSNIT Employer Portion (%)',
        compute='_compute_ssnit_employer_portion',
        help='Employer portion going to SSNIT (Employer Rate - Tier 2)',
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    @api.depends('ssnit_employer_rate', 'tier2_rate')
    def _compute_ssnit_employer_portion(self):
        for config in self:
            config.ssnit_employer_portion = config.ssnit_employer_rate - config.tier2_rate

    @api.model
    def get_config(self, company=None):
        """Get active configuration for company."""
        company = company or self.env.company
        config = self.search([
            ('active', '=', True),
            '|', ('company_id', '=', company.id), ('company_id', '=', False)
        ], limit=1)
        return config

    def calculate_ssnit_employee(self, basic_salary):
        """Calculate SSNIT Tier 1 employee contribution."""
        self.ensure_one()
        return round(basic_salary * (self.ssnit_employee_rate / 100), 2)

    def calculate_ssnit_employer(self, basic_salary):
        """Calculate SSNIT employer contribution (excluding Tier 2)."""
        self.ensure_one()
        return round(basic_salary * (self.ssnit_employer_portion / 100), 2)

    def calculate_tier2(self, basic_salary):
        """Calculate Tier 2 pension contribution."""
        self.ensure_one()
        return round(basic_salary * (self.tier2_rate / 100), 2)

    def calculate_total_employer_pension(self, basic_salary):
        """Calculate total employer pension contribution (SSNIT + Tier 2)."""
        self.ensure_one()
        return round(basic_salary * (self.ssnit_employer_rate / 100), 2)
