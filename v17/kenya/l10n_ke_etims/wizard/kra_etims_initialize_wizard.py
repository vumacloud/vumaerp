# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class KRAeTIMSInitializeWizard(models.TransientModel):
    _name = 'kra.etims.initialize.wizard'
    _description = 'KRA e-TIMS Device Initialization Wizard'

    name = fields.Char(
        string='Device Name',
        required=True,
        default='Main OSCU Device'
    )
    
    device_serial = fields.Char(
        string='Device Serial Number',
        required=True,
        help='Serial number provided by KRA for your OSCU device'
    )
    
    tin = fields.Char(
        string='Company TIN',
        required=True,
        default=lambda self: self.env.company.vat or self.env.company.kra_etims_tin,
        help='Tax Identification Number registered with KRA'
    )
    
    bhf_id = fields.Char(
        string='Branch ID',
        required=True,
        default='00',
        help='Branch Identification Code (00 for main branch)'
    )
    
    cmc_key = fields.Char(
        string='CMC Key',
        required=True,
        help='Communication Key obtained from KRA during initialization'
    )
    
    base_url = fields.Char(
        string='e-TIMS API URL',
        required=True,
        default='https://etims-sbx.kra.go.ke/etims-api',
        help='Base URL for e-TIMS API'
    )
    
    def action_initialize(self):
        """Initialize device and configure company settings"""
        self.ensure_one()
        
        # Create device record
        device = self.env['kra.etims.device'].create({
            'name': self.name,
            'device_serial': self.device_serial,
            'tin': self.tin,
            'bhf_id': self.bhf_id,
            'company_id': self.env.company.id,
        })
        
        # Update company settings
        self.env.company.write({
            'kra_etims_enabled': True,
            'kra_etims_base_url': self.base_url,
            'kra_etims_tin': self.tin,
            'kra_etims_bhf_id': self.bhf_id,
            'kra_etims_device_serial': self.device_serial,
            'kra_etims_cmc_key': self.cmc_key,
        })
        
        # Initialize device with KRA
        try:
            device.action_initialize()
            
            # Sync codes
            device.action_sync_codes()
            
        except Exception as e:
            raise UserError(_('Initialization failed: %s') % str(e))
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kra.etims.device',
            'res_id': device.id,
            'view_mode': 'form',
            'target': 'current',
        }
