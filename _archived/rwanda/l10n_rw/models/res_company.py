# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    # RRA (Rwanda Revenue Authority) Information
    rra_tin = fields.Char(
        string='RRA TIN',
        help='Rwanda Revenue Authority Tax Identification Number'
    )
    rra_vat_registered = fields.Boolean(
        string='VAT Registered',
        default=False,
        help='Check if company is registered for VAT with RRA'
    )
    ebm_device_id = fields.Char(
        string='EBM Device ID',
        help='Electronic Billing Machine device identifier'
    )
    ebm_api_key = fields.Char(
        string='EBM API Key',
        help='API key for EBM integration'
    )

    # RSSB (Rwanda Social Security Board) Information
    rssb_employer_code = fields.Char(
        string='RSSB Employer Code',
        help='Rwanda Social Security Board employer registration code'
    )
