# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class NigeriaFIRSConfig(models.Model):
    _name = 'nigeria.firs.config'
    _description = 'Nigeria FIRS Configuration'
    _rec_name = 'name'

    name = fields.Char(string='Configuration Name', required=True, default='Default')
    active = fields.Boolean(default=True)

    # FIRS Credentials
    tin = fields.Char(
        string='TIN',
        required=True,
        help='Tax Identification Number',
    )
    rc_number = fields.Char(
        string='RC Number',
        help='Corporate Affairs Commission registration number',
    )
    vat_registered = fields.Boolean(
        string='VAT Registered',
        default=False,
    )
    vat_reg_number = fields.Char(
        string='VAT Reg Number',
        help='VAT registration number (if registered)',
    )

    # Company size classification
    company_size = fields.Selection([
        ('small', 'Small (Turnover < NGN 25M)'),
        ('medium', 'Medium (NGN 25M - 100M)'),
        ('large', 'Large (> NGN 100M)'),
    ], string='Company Size', default='medium')

    # CIT Rate based on size
    cit_rate = fields.Float(
        string='CIT Rate (%)',
        compute='_compute_cit_rate',
        store=True,
    )

    # TCC Info
    tcc_number = fields.Char(string='TCC Number')
    tcc_expiry = fields.Date(string='TCC Expiry Date')
    tcc_valid = fields.Boolean(
        string='TCC Valid',
        compute='_compute_tcc_valid',
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    @api.depends('company_size')
    def _compute_cit_rate(self):
        for config in self:
            if config.company_size == 'small':
                config.cit_rate = 0.0
            elif config.company_size == 'medium':
                config.cit_rate = 20.0
            else:
                config.cit_rate = 30.0

    @api.depends('tcc_expiry')
    def _compute_tcc_valid(self):
        today = fields.Date.today()
        for config in self:
            config.tcc_valid = config.tcc_expiry and config.tcc_expiry >= today

    @api.model
    def get_config(self, company=None):
        """Get active FIRS configuration for company."""
        company = company or self.env.company
        config = self.search([
            ('active', '=', True),
            '|', ('company_id', '=', company.id), ('company_id', '=', False)
        ], limit=1)
        return config
