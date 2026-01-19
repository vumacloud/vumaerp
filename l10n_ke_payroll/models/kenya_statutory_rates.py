# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class KenyaSHIFRate(models.Model):
    """SHA Social Health Insurance Fund - replaced NHIF in October 2024"""
    _name = 'kenya.shif.rate'
    _description = 'Kenya SHIF (SHA) Contribution Rates'

    name = fields.Char(string='Name', default='SHIF Rate')
    rate = fields.Float(string='Rate (%)', default=2.75, help='SHIF rate as percentage of gross salary')
    min_contribution = fields.Float(string='Minimum Contribution', default=300, help='Minimum monthly contribution (KES 300)')
    active = fields.Boolean(default=True)
    effective_date = fields.Date(string='Effective Date', default='2024-10-01')

    @api.model
    def get_contribution(self, gross_salary):
        """Get SHIF contribution for a given gross salary.

        SHIF (Social Health Insurance Fund) replaced NHIF in October 2024.
        Rate: 2.75% of gross salary with minimum KES 300, no maximum cap.
        """
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            # Default rates if no config
            rate = 2.75
            min_contrib = 300
        else:
            rate = config.rate
            min_contrib = config.min_contribution

        contribution = gross_salary * (rate / 100)
        return max(contribution, min_contrib)


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

    name = fields.Char(string='Name', required=True, default='Kenya Statutory Rates 2025')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)
    is_active = fields.Boolean(related='active', string='Is Active')

    # Personal Relief
    personal_relief = fields.Float(
        string='Personal Relief (Monthly)',
        default=2400.0,
        help='Monthly personal relief deduction (KES 2,400)',
    )
    insurance_relief_rate = fields.Float(
        string='Insurance Relief Rate (%)',
        default=15.0,
        help='Insurance relief rate on SHIF contribution (15%)',
    )
    max_insurance_relief = fields.Float(
        string='Max Insurance Relief (Monthly)',
        default=5000.0,
        help='Maximum monthly insurance relief (KES 5,000)',
    )

    # SHIF (SHA) - replaced NHIF Oct 2024
    shif_rate = fields.Float(
        string='SHIF Rate (%)',
        default=2.75,
        help='Social Health Insurance Fund rate (2.75% of gross)',
    )
    shif_min = fields.Float(
        string='SHIF Minimum',
        default=300.0,
        help='Minimum monthly SHIF contribution (KES 300)',
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
            config = self.create({
                'name': f'Kenya Statutory Rates - {company.name}',
                'company_id': company.id,
            })
        return config

    def calculate_shif(self, gross_salary):
        """Calculate SHIF (SHA) contribution - replaced NHIF in Oct 2024."""
        self.ensure_one()
        contribution = gross_salary * (self.shif_rate / 100)
        return max(contribution, self.shif_min)

    def calculate_nssf(self, gross_salary):
        """Calculate NSSF contribution (employee portion)."""
        self.ensure_one()
        tier1_pensionable = min(gross_salary, self.nssf_tier1_limit)
        tier1_contribution = tier1_pensionable * (self.nssf_rate / 100)

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

    def calculate_insurance_relief(self, shif_contribution):
        """Calculate insurance relief on SHIF."""
        self.ensure_one()
        relief = shif_contribution * (self.insurance_relief_rate / 100)
        return min(relief, self.max_insurance_relief)
