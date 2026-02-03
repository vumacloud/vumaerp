# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EvatConfig(models.Model):
    _name = 'evat.config'
    _description = 'Ghana E-VAT Configuration'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)

    # Environment
    environment = fields.Selection([
        ('sandbox', 'Sandbox (Testing)'),
        ('production', 'Production'),
    ], string='Environment', default='sandbox', required=True)

    # API Configuration
    api_url = fields.Char(string='API URL')
    api_key = fields.Char(string='API Key')
    api_secret = fields.Char(string='API Secret')

    # Company Tax Info
    tin = fields.Char(string='TIN', size=11, required=True)
    vat_number = fields.Char(string='VAT Number')

    # Settings
    auto_submit = fields.Boolean(
        string='Auto-submit Invoices',
        default=False,
        help='Automatically submit invoices to E-VAT on validation'
    )

    # Status
    last_sync = fields.Datetime(string='Last Sync')
    status = fields.Selection([
        ('draft', 'Not Configured'),
        ('active', 'Active'),
        ('error', 'Error'),
    ], string='Status', default='draft')

    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one E-VAT configuration per company allowed.')
    ]

    @api.model
    def get_config(self, company=None):
        """Get E-VAT configuration for company."""
        company = company or self.env.company
        config = self.search([('company_id', '=', company.id)], limit=1)
        if not config:
            raise UserError(_('E-VAT is not configured for %s.') % company.name)
        return config
