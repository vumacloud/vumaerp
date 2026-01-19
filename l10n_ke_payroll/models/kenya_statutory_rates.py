# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class KenyaNHIFRate(models.Model):
    _name = 'kenya.nhif.rate'
    _description = 'Kenya NHIF Contribution Rates'
    _order = 'min_salary'

    name = fields.Char(string='Band Name', compute='_compute_name', store=True)
    min_salary = fields.Float(string='Minimum Salary', required=True)
    max_salary = fields.Float(string='Maximum Salary', required=True)
    contribution = fields.Float(string='Monthly Contribution', required=True)
    active = fields.Boolean(default=True)
    effective_date = fields.Date(string='Effective Date', default=fields.Date.today)

    @api.depends('min_salary', 'max_salary', 'contribution')
    def _compute_name(self):
        for rate in self:
            if rate.max_salary == 0 or rate.max_salary > 100000000:
                rate.name = f"KES {rate.min_salary:,.0f}+ → KES {rate.contribution:,.0f}"
            else:
                rate.name = f"KES {rate.min_salary:,.0f} - {rate.max_salary:,.0f} → KES {rate.contribution:,.0f}"

    @api.model
    def get_contribution(self, gross_salary):
        """Get NHIF contribution for a given gross salary."""
        rate = self.search([
            ('min_salary', '<=', gross_salary),
            ('max_salary', '>=', gross_salary),
            ('active', '=', True),
        ], limit=1)

        if not rate:
            # Get highest band if salary exceeds all bands
            rate = self.search([('active', '=', True)], order='max_salary desc', limit=1)

        return rate.contribution if rate else 0.0


class KenyaPAYETaxBand(models.Model):
    _name = 'kenya.paye.tax.band'
    _description = 'Kenya PAYE Tax Bands'
    _order = 'min_income'

    name = fields.Char(string='Band Name', compute='_compute_name', store=True)
    min_income = fields.Float(string='Minimum Income', required=True)
    max_income = fields.Float(string='Maximum Income', required=True)
    rate = fields.Float(string='Tax Rate (%)', required=True)
    active = fields.Boolean(default=True)
    effective_date = fields.Date(string='Effective Date', default=fields.Date.today)
    band_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ], string='Band Type', default='monthly', required=True)

    @api.depends('min_income', 'max_income', 'rate')
    def _compute_name(self):
        for band in self:
            if band.max_income == 0 or band.max_income > 100000000:
                band.name = f"KES {band.min_income:,.0f}+ @ {band.rate}%"
            else:
                band.name = f"KES {band.min_income:,.0f} - {band.max_income:,.0f} @ {band.rate}%"

    @api.model
    def calculate_paye(self, taxable_income, band_type='monthly'):
        """Calculate PAYE tax for a given taxable income."""
        bands = self.search([
            ('active', '=', True),
            ('band_type', '=', band_type),
        ], order='min_income')

        if not bands:
            return 0.0

        total_tax = 0.0
        remaining_income = taxable_income

        for band in bands:
            if remaining_income <= 0:
                break

            band_range = band.max_income - band.min_income
            if band.max_income == 0 or band.max_income > 100000000:
                # Last band - tax all remaining income
                taxable_in_band = remaining_income
            else:
                taxable_in_band = min(remaining_income, band_range)

            tax_in_band = taxable_in_band * (band.rate / 100)
            total_tax += tax_in_band
            remaining_income -= taxable_in_band

        return total_tax


class KenyaStatutoryConfig(models.Model):
    _name = 'kenya.statutory.config'
    _description = 'Kenya Statutory Configuration'

    name = fields.Char(string='Name', required=True, default='Kenya Statutory Rates')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)

    # Personal Relief
    personal_relief = fields.Float(
        string='Personal Relief (Monthly)',
        default=2400.0,
        help='Monthly personal relief deduction (KES 2,400)',
    )
    insurance_relief_rate = fields.Float(
        string='Insurance Relief Rate (%)',
        default=15.0,
        help='Insurance relief rate on NHIF contribution (15%)',
    )
    max_insurance_relief = fields.Float(
        string='Max Insurance Relief (Monthly)',
        default=5000.0,
        help='Maximum monthly insurance relief (KES 5,000)',
    )

    # NSSF Rates
    nssf_tier1_limit = fields.Float(
        string='NSSF Tier I Limit',
        default=7000.0,
        help='Upper limit for Tier I pension contribution (KES 7,000)',
    )
    nssf_tier2_limit = fields.Float(
        string='NSSF Tier II Limit',
        default=36000.0,
        help='Upper limit for Tier II pension (KES 36,000 cumulative)',
    )
    nssf_rate = fields.Float(
        string='NSSF Rate (%)',
        default=6.0,
        help='NSSF contribution rate (6%)',
    )

    # Housing Levy
    housing_levy_rate = fields.Float(
        string='Housing Levy Rate (%)',
        default=1.5,
        help='Affordable Housing Levy rate (1.5%)',
    )

    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one statutory configuration per company is allowed.'),
    ]

    @api.model
    def get_config(self, company=None):
        """Get statutory configuration for the company."""
        company = company or self.env.company
        config = self.search([('company_id', '=', company.id), ('active', '=', True)], limit=1)
        if not config:
            # Create default configuration
            config = self.create({
                'name': f'Kenya Statutory Rates - {company.name}',
                'company_id': company.id,
            })
        return config

    def calculate_nssf(self, gross_salary):
        """Calculate NSSF contribution (employee portion)."""
        self.ensure_one()

        # Tier I: 6% on first 7,000
        tier1_pensionable = min(gross_salary, self.nssf_tier1_limit)
        tier1_contribution = tier1_pensionable * (self.nssf_rate / 100)

        # Tier II: 6% on amount between 7,000 and 36,000
        if gross_salary > self.nssf_tier1_limit:
            tier2_pensionable = min(gross_salary, self.nssf_tier2_limit) - self.nssf_tier1_limit
            tier2_contribution = tier2_pensionable * (self.nssf_rate / 100)
        else:
            tier2_contribution = 0.0

        return tier1_contribution + tier2_contribution

    def calculate_housing_levy(self, gross_salary):
        """Calculate Housing Levy contribution."""
        self.ensure_one()
        return gross_salary * (self.housing_levy_rate / 100)

    def calculate_insurance_relief(self, nhif_contribution):
        """Calculate insurance relief on NHIF."""
        self.ensure_one()
        relief = nhif_contribution * (self.insurance_relief_rate / 100)
        return min(relief, self.max_insurance_relief)
