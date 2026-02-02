# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    # EBM Configuration
    ebm_enabled = fields.Boolean(
        string='Enable EBM',
        default=False,
        help='Enable Electronic Billing Machine integration'
    )
    ebm_environment = fields.Selection([
        ('sandbox', 'Sandbox (Testing)'),
        ('production', 'Production'),
    ], string='EBM Environment', default='sandbox')

    ebm_device_id = fields.Char(
        string='EBM Device ID',
        help='Registered EBM device identifier from RRA'
    )
    ebm_serial_number = fields.Char(
        string='EBM Serial Number',
        help='EBM device serial number'
    )

    # API Credentials
    ebm_api_url = fields.Char(
        string='EBM API URL',
        default='https://efiling.rra.gov.rw/ebmsapi/api'
    )
    ebm_api_username = fields.Char(
        string='EBM API Username'
    )
    ebm_api_password = fields.Char(
        string='EBM API Password'
    )

    # Business Information
    rra_tin = fields.Char(
        string='RRA TIN',
        help='Tax Identification Number registered with RRA'
    )
    vsd_c = fields.Char(
        string='VSDC ID',
        help='Virtual SDC (Software Device Controller) ID'
    )
