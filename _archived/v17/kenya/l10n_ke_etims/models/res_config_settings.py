# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # KRA e-TIMS Configuration
    kra_etims_enabled = fields.Boolean(
        string='Enable KRA e-TIMS',
        related='company_id.kra_etims_enabled',
        readonly=False,
        help='Enable integration with Kenya Revenue Authority e-TIMS system'
    )
    
    kra_etims_base_url = fields.Char(
        string='e-TIMS API URL',
        related='company_id.kra_etims_base_url',
        readonly=False,
        help='Base URL for e-TIMS API (Sandbox or Production)'
    )
    
    kra_etims_tin = fields.Char(
        string='Company TIN',
        related='company_id.kra_etims_tin',
        readonly=False,
        help='Tax Identification Number registered with KRA'
    )
    
    kra_etims_bhf_id = fields.Char(
        string='Branch ID',
        related='company_id.kra_etims_bhf_id',
        readonly=False,
        help='Branch Identification Code (e.g., 00 for main branch)'
    )
    
    kra_etims_device_serial = fields.Char(
        string='Device Serial Number',
        related='company_id.kra_etims_device_serial',
        readonly=False,
        help='Serial number of the registered OSCU device'
    )
    
    kra_etims_cmc_key = fields.Char(
        string='CMC Key',
        related='company_id.kra_etims_cmc_key',
        readonly=False,
        help='Communication Key obtained from KRA during device initialization'
    )
    
    kra_etims_auto_submit = fields.Boolean(
        string='Auto-Submit Invoices',
        related='company_id.kra_etims_auto_submit',
        readonly=False,
        help='Automatically submit invoices to e-TIMS when validated'
    )
    
    kra_etims_invoice_counter = fields.Integer(
        string='Invoice Counter',
        related='company_id.kra_etims_invoice_counter',
        readonly=False,
        help='Current invoice counter for e-TIMS submission'
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    kra_etims_enabled = fields.Boolean(
        string='Enable KRA e-TIMS',
        default=False
    )
    
    kra_etims_base_url = fields.Char(
        string='e-TIMS API URL',
        default='https://etims-sbx.kra.go.ke/etims-api',
        help='Sandbox: https://etims-sbx.kra.go.ke/etims-api\n'
             'Production: https://etims.kra.go.ke/etims-api'
    )
    
    kra_etims_tin = fields.Char(
        string='Company TIN',
        help='Tax Identification Number'
    )
    
    kra_etims_bhf_id = fields.Char(
        string='Branch ID',
        default='00',
        help='Branch Identification Code'
    )
    
    kra_etims_device_serial = fields.Char(
        string='Device Serial Number'
    )
    
    kra_etims_cmc_key = fields.Char(
        string='CMC Key',
        help='Communication Key from KRA for API authentication'
    )
    
    kra_etims_auto_submit = fields.Boolean(
        string='Auto-Submit Invoices',
        default=False
    )
    
    kra_etims_invoice_counter = fields.Integer(
        string='Invoice Counter',
        default=1,
        help='Sequential counter for e-TIMS invoice numbers'
    )
    
    @api.model
    def get_next_kra_invoice_number(self):
        """Get and increment the KRA invoice counter"""
        self.ensure_one()
        current = self.kra_etims_invoice_counter
        self.kra_etims_invoice_counter = current + 1
        return current
