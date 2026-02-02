# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class KRAeTIMSDevice(models.Model):
    _name = 'kra.etims.device'
    _description = 'KRA e-TIMS Device'
    _order = 'create_date desc'

    name = fields.Char(
        string='Device Name',
        required=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    device_serial = fields.Char(
        string='Device Serial Number',
        required=True
    )
    
    tin = fields.Char(
        string='TIN',
        required=True
    )
    
    bhf_id = fields.Char(
        string='Branch ID',
        required=True,
        default='00'
    )
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('initialized', 'Initialized'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], string='Status', default='draft', required=True)
    
    initialization_date = fields.Datetime(
        string='Initialization Date',
        readonly=True
    )
    
    last_sync_date = fields.Datetime(
        string='Last Sync Date',
        readonly=True
    )
    
    notes = fields.Text(
        string='Notes'
    )
    
    # Device information from KRA
    kra_result_cd = fields.Char(
        string='Result Code',
        readonly=True
    )
    
    kra_result_msg = fields.Text(
        string='Result Message',
        readonly=True
    )
    
    kra_result_dt = fields.Char(
        string='Result DateTime',
        readonly=True
    )
    
    def action_initialize(self):
        """Initialize device with KRA e-TIMS"""
        self.ensure_one()
        
        api = self.env['kra.etims.api']
        
        try:
            result = api.initialize_device(
                device_serial=self.device_serial,
                tin=self.tin,
                bhf_id=self.bhf_id
            )
            
            self.write({
                'status': 'initialized',
                'initialization_date': fields.Datetime.now(),
                'kra_result_cd': result.get('resultCd'),
                'kra_result_msg': result.get('resultMsg'),
                'kra_result_dt': result.get('resultDt'),
            })
            
            # Update company settings
            self.company_id.write({
                'kra_etims_device_serial': self.device_serial,
                'kra_etims_tin': self.tin,
                'kra_etims_bhf_id': self.bhf_id,
                'kra_etims_enabled': True,
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Device initialized successfully with KRA e-TIMS'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(_('Device initialization failed: %s') % str(e))
    
    def action_activate(self):
        """Activate device"""
        self.ensure_one()
        self.status = 'active'
    
    def action_deactivate(self):
        """Deactivate device"""
        self.ensure_one()
        self.status = 'inactive'
    
    def action_sync_codes(self):
        """Sync codes from KRA e-TIMS"""
        self.ensure_one()
        
        api = self.env['kra.etims.api']
        
        # Sync Item Classifications
        try:
            result = api.select_codes('01')  # Item Classification
            classifications = result.get('data', {}).get('clsList', [])
            
            ClassificationModel = self.env['kra.etims.classification']
            for cls_data in classifications:
                existing = ClassificationModel.search([
                    ('code', '=', cls_data.get('cdCls')),
                    ('item_code', '=', cls_data.get('cd')),
                ], limit=1)
                
                vals = {
                    'code': cls_data.get('cdCls'),
                    'item_code': cls_data.get('cd'),
                    'name': cls_data.get('cdNm'),
                    'description': cls_data.get('cdDesc'),
                    'level': cls_data.get('lvl'),
                    'parent_code': cls_data.get('upperCd'),
                    'use_yn': cls_data.get('useYn') == 'Y',
                }
                
                if existing:
                    existing.write(vals)
                else:
                    ClassificationModel.create(vals)
            
            self.last_sync_date = fields.Datetime.now()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Codes synchronized successfully'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(_('Code synchronization failed: %s') % str(e))
