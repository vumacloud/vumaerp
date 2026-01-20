# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class UgandaPAYETaxBand(models.Model):
    _name = 'uganda.paye.tax.band'
    _description = 'Uganda PAYE Tax Bands'
    _order = 'min_income'

    name = fields.Char(string='Band Name', compute='_compute_name', store=True)
    min_income = fields.Float(string='Minimum Income (UGX)', required=True)
    max_income = fields.Float(string='Maximum Income (UGX)', required=True)
    rate = fields.Float(string='Tax Rate (%)', required=True)
    resident_type = fields.Selection([
        ('resident', 'Resident'),
        ('non_resident', 'Non-Resident'),
    ], string='Resident Type', default='resident', required=True)
    active = fields.Boolean(default=True)
    band_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ], string='Band Type', default='monthly', required=True)

    @api.depends('min_income', 'max_income', 'rate')
    def _compute_name(self):
        for band in self:
            if band.max_income == 0 or band.max_income > 999999999:
                band.name = f"UGX {band.min_income:,.0f}+ @ {band.rate}%"
            else:
                band.name = f"UGX {band.min_income:,.0f} - {band.max_income:,.0f} @ {band.rate}%"

    @api.model
    def calculate_paye(self, taxable_income, resident_type='resident', band_type='monthly'):
        """Calculate PAYE tax using progressive tax bands."""
        bands = self.search([
            ('active', '=', True),
            ('resident_type', '=', resident_type),
            ('band_type', '=', band_type),
        ], order='min_income')

        if not bands:
            return 0.0

        total_tax = 0.0
        remaining_income = taxable_income

        for band in bands:
            if remaining_income <= 0:
                break

            # Calculate taxable amount in this band
            if band.min_income >= taxable_income:
                break

            band_ceiling = band.max_income if band.max_income > 0 and band.max_income < 999999999 else taxable_income
            taxable_in_band = min(remaining_income, band_ceiling - band.min_income)

            if taxable_in_band > 0:
                tax_in_band = taxable_in_band * (band.rate / 100)
                total_tax += tax_in_band
                remaining_income -= taxable_in_band

        return round(total_tax, 0)


class UgandaLSTRate(models.Model):
    _name = 'uganda.lst.rate'
    _description = 'Uganda Local Service Tax Rates'
    _order = 'min_income'

    name = fields.Char(string='Name', required=True)
    local_government = fields.Char(string='Local Government', default='Kampala')
    min_income = fields.Float(string='Minimum Annual Income (UGX)', required=True)
    max_income = fields.Float(string='Maximum Annual Income (UGX)', required=True)
    annual_tax = fields.Float(string='Annual LST (UGX)', required=True)
    active = fields.Boolean(default=True)

    @api.model
    def get_lst_amount(self, annual_income, local_government='Kampala'):
        """Get LST amount for given annual income."""
        rate = self.search([
            ('active', '=', True),
            ('local_government', '=', local_government),
            ('min_income', '<=', annual_income),
            '|',
            ('max_income', '>=', annual_income),
            ('max_income', '=', 0),
        ], limit=1, order='min_income desc')

        if rate:
            return rate.annual_tax
        return 0.0


class UgandaStatutoryConfig(models.Model):
    _name = 'uganda.statutory.config'
    _description = 'Uganda Statutory Configuration'

    name = fields.Char(string='Name', required=True, default='Uganda Statutory Rates 2025')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)

    # NSSF Rates
    nssf_employee_rate = fields.Float(
        string='NSSF Employee Rate (%)',
        default=5.0,
        help='Employee NSSF contribution rate (5%)',
    )
    nssf_employer_rate = fields.Float(
        string='NSSF Employer Rate (%)',
        default=10.0,
        help='Employer NSSF contribution rate (10%)',
    )

    # PAYE threshold
    paye_threshold = fields.Float(
        string='PAYE Threshold (Monthly)',
        default=235000.0,
        help='Monthly income below which no PAYE is charged (UGX 235,000)',
    )

    # LST
    lst_local_government = fields.Char(
        string='Local Government',
        default='Kampala',
        help='Local government for LST calculation',
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
                'name': f'Uganda Statutory Rates - {company.name}',
                'company_id': company.id,
            })
        return config

    def calculate_nssf_employee(self, gross_salary):
        """Calculate employee NSSF contribution."""
        self.ensure_one()
        return round(gross_salary * (self.nssf_employee_rate / 100), 0)

    def calculate_nssf_employer(self, gross_salary):
        """Calculate employer NSSF contribution."""
        self.ensure_one()
        return round(gross_salary * (self.nssf_employer_rate / 100), 0)

    def calculate_lst_monthly(self, annual_income):
        """Calculate monthly LST installment (paid July-October)."""
        self.ensure_one()
        annual_lst = self.env['uganda.lst.rate'].get_lst_amount(
            annual_income, self.lst_local_government
        )
        # LST is paid in 4 installments
        return round(annual_lst / 4, 0)
