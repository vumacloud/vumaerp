# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # KRA e-TIMS Fields
    kra_customer_type = fields.Selection([
        ('B2B', 'Business to Business (B2B)'),
        ('B2C', 'Business to Consumer (B2C)'),
    ], string='Customer Type',
       help='Type of customer for e-TIMS classification')
    
    kra_pin = fields.Char(
        string='KRA PIN',
        help='Kenya Revenue Authority Personal Identification Number'
    )
    
    # Override vat field for TIN
    vat = fields.Char(
        help='Tax Identification Number. For Kenyan entities, use the KRA PIN.'
    )
    
    @api.onchange('vat')
    def _onchange_vat_sync_pin(self):
        """Sync VAT to KRA PIN for Kenyan partners"""
        if self.country_id.code == 'KE' and self.vat:
            self.kra_pin = self.vat
    
    @api.onchange('kra_pin')
    def _onchange_pin_sync_vat(self):
        """Sync KRA PIN to VAT"""
        if self.kra_pin and self.country_id.code == 'KE':
            self.vat = self.kra_pin
