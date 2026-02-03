# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class KenyaStatutoryConfig(models.Model):
    _name = 'kenya.statutory.config'
    _description = 'Kenya Statutory Rates Configuration'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)

    # NSSF Rates (Effective Feb 2024)
    nssf_tier1_limit = fields.Float(
        string='NSSF Tier I Limit',
        default=7000.0,
        help='Upper limit for Tier I contributions'
    )
    nssf_tier2_limit = fields.Float(
        string='NSSF Tier II Upper Limit',
        default=36000.0,
        help='Upper limit for Tier II contributions'
    )
    nssf_rate = fields.Float(
        string='NSSF Rate (%)',
        default=6.0,
        help='NSSF contribution rate for both tiers'
    )

    # SHIF Rate (Effective Oct 2024)
    shif_rate = fields.Float(
        string='SHIF Rate (%)',
        default=2.75,
        help='Social Health Insurance Fund rate'
    )

    # Housing Levy
    housing_levy_rate = fields.Float(
        string='Housing Levy Rate (%)',
        default=1.5,
        help='Affordable Housing Levy rate'
    )

    # Personal Relief
    personal_relief = fields.Float(
        string='Personal Relief (Monthly)',
        default=2400.0,
        help='Monthly personal relief amount'
    )

    # Insurance Relief
    insurance_relief_rate = fields.Float(
        string='Insurance Relief Rate (%)',
        default=15.0,
        help='Rate for calculating insurance relief on SHIF'
    )
    insurance_relief_max = fields.Float(
        string='Max Insurance Relief (Monthly)',
        default=5000.0,
        help='Maximum monthly insurance relief'
    )

    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one configuration per company allowed.')
    ]

    @api.model
    def get_config(self, company=None):
        """Get statutory configuration for company."""
        company = company or self.env.company
        config = self.search([('company_id', '=', company.id)], limit=1)
        if not config:
            config = self.create({'company_id': company.id})
        return config

    def calculate_nssf(self, gross):
        """Calculate NSSF contribution (employee or employer - same amount)."""
        self.ensure_one()
        rate = self.nssf_rate / 100

        # Tier I: 6% of first KES 7,000
        tier1 = min(gross, self.nssf_tier1_limit) * rate

        # Tier II: 6% of (gross - 7,000), capped at (36,000 - 7,000)
        if gross > self.nssf_tier1_limit:
            tier2_base = min(gross, self.nssf_tier2_limit) - self.nssf_tier1_limit
            tier2 = tier2_base * rate
        else:
            tier2 = 0

        return round(tier1 + tier2, 2)

    def calculate_shif(self, gross):
        """Calculate SHIF contribution."""
        self.ensure_one()
        return round(gross * (self.shif_rate / 100), 2)

    def calculate_housing_levy(self, gross):
        """Calculate Housing Levy."""
        self.ensure_one()
        return round(gross * (self.housing_levy_rate / 100), 2)

    def calculate_insurance_relief(self, shif_amount):
        """Calculate insurance relief on SHIF contribution."""
        self.ensure_one()
        relief = shif_amount * (self.insurance_relief_rate / 100)
        return round(min(relief, self.insurance_relief_max), 2)
