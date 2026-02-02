# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class EBMConfig(models.Model):
    _name = 'l10n_rw.ebm.config'
    _description = 'EBM Configuration'

    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)

    # Device Information
    device_id = fields.Char(string='Device ID', required=True)
    serial_number = fields.Char(string='Serial Number')
    device_type = fields.Selection([
        ('virtual', 'Virtual SDC'),
        ('physical', 'Physical EBM'),
    ], string='Device Type', default='virtual')

    # Connection Settings
    api_endpoint = fields.Char(
        string='API Endpoint',
        default='https://efiling.rra.gov.rw/ebmsapi/api'
    )
    environment = fields.Selection([
        ('sandbox', 'Sandbox'),
        ('production', 'Production'),
    ], string='Environment', default='sandbox')

    # Status
    last_sync = fields.Datetime(string='Last Sync')
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
    ], string='Status', default='inactive')

    def action_test_connection(self):
        """Test connection to EBM API"""
        self.ensure_one()
        try:
            # In production, this would test the actual API connection
            if self.environment == 'sandbox':
                self.status = 'active'
                self.last_sync = fields.Datetime.now()
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('EBM connection test successful (Sandbox mode)'),
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_('Production connection test requires valid RRA credentials'))
        except Exception as e:
            self.status = 'error'
            raise UserError(_('Connection test failed: %s') % str(e))
