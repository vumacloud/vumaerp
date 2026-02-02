# -*- coding: utf-8 -*-
from odoo import api, fields, models


class GhanaStatutoryConfig(models.Model):
    _name = 'ghana.statutory.config'
    _description = 'Ghana Statutory Rates Configuration'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)

    # SSNIT Rates
    ssnit_employee_rate = fields.Float(
        string='SSNIT Employee Rate (%)',
        default=5.5,
        help='Employee contribution rate to SSNIT'
    )
    ssnit_employer_rate = fields.Float(
        string='SSNIT Employer Rate (%)',
        default=13.0,
        help='Employer contribution rate to SSNIT'
    )

    # Tier 2 Pension
    tier2_rate = fields.Float(
        string='Tier 2 Rate (%)',
        default=5.0,
        help='Tier 2 pension contribution rate'
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

    def calculate_ssnit_employee(self, basic):
        """Calculate SSNIT employee contribution."""
        self.ensure_one()
        return round(basic * (self.ssnit_employee_rate / 100), 2)

    def calculate_ssnit_employer(self, basic):
        """Calculate SSNIT employer contribution."""
        self.ensure_one()
        return round(basic * (self.ssnit_employer_rate / 100), 2)

    def calculate_tier2(self, basic):
        """Calculate Tier 2 pension contribution."""
        self.ensure_one()
        return round(basic * (self.tier2_rate / 100), 2)
