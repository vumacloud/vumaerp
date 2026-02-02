# -*- coding: utf-8 -*-
import logging
import json
import hashlib
import requests
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class GhanaEVATConfig(models.Model):
    _name = 'ghana.evat.config'
    _description = 'Ghana GRA E-VAT Configuration'
    _rec_name = 'name'

    name = fields.Char(string='Configuration Name', required=True, default='Default')
    active = fields.Boolean(default=True)

    # GRA Credentials
    tin = fields.Char(
        string='TIN',
        required=True,
        help='Ghana Revenue Authority Taxpayer Identification Number',
    )
    branch_code = fields.Char(
        string='Branch Code',
        default='001',
        help='Business branch code',
    )
    device_serial = fields.Char(
        string='Device Serial',
        help='E-VAT device serial number',
    )

    # API Configuration
    environment = fields.Selection([
        ('sandbox', 'Sandbox/Testing'),
        ('production', 'Production'),
    ], string='Environment', default='sandbox', required=True)

    api_url = fields.Char(
        string='API URL',
        compute='_compute_api_url',
        store=True,
    )
    api_key = fields.Char(
        string='API Key',
        help='GRA API authentication key',
    )
    api_secret = fields.Char(
        string='API Secret',
        help='GRA API secret for signing requests',
    )

    # Status
    is_registered = fields.Boolean(
        string='Device Registered',
        default=False,
    )
    last_sync = fields.Datetime(string='Last Sync')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    @api.depends('environment')
    def _compute_api_url(self):
        for config in self:
            if config.environment == 'production':
                config.api_url = 'https://evat.gra.gov.gh/api/v1'
            else:
                config.api_url = 'https://sandbox.evat.gra.gov.gh/api/v1'

    @api.model
    def get_config(self, company=None):
        """Get active E-VAT configuration for company."""
        company = company or self.env.company
        config = self.search([
            ('active', '=', True),
            '|', ('company_id', '=', company.id), ('company_id', '=', False)
        ], limit=1)

        if not config:
            raise UserError(_("No active Ghana E-VAT configuration found. Please configure E-VAT settings."))

        return config

    def _generate_signature(self, payload):
        """Generate signature for API request."""
        self.ensure_one()
        if not self.api_secret:
            raise UserError(_("API Secret is not configured."))

        message = json.dumps(payload, sort_keys=True)
        signature = hashlib.sha256(
            (message + self.api_secret).encode()
        ).hexdigest()
        return signature

    def _get_headers(self):
        """Get API request headers."""
        self.ensure_one()
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'X-TIN': self.tin,
            'X-Device-Serial': self.device_serial or '',
        }

    def _make_request(self, endpoint, method='POST', data=None):
        """Make API request to GRA E-VAT system."""
        self.ensure_one()

        url = f"{self.api_url}/{endpoint}"
        headers = self._get_headers()

        if data:
            headers['X-Signature'] = self._generate_signature(data)

        try:
            if method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            else:
                raise UserError(_("Unsupported HTTP method: %s") % method)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise UserError(_("Connection to GRA E-VAT timed out. Please try again."))
        except requests.exceptions.ConnectionError:
            raise UserError(_("Could not connect to GRA E-VAT. Check your internet connection."))
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_data = e.response.json()
                error_msg = error_data.get('message', str(e))
            except Exception:
                pass
            raise UserError(_("GRA E-VAT Error: %s") % error_msg)

    def action_test_connection(self):
        """Test connection to GRA E-VAT API."""
        self.ensure_one()

        try:
            result = self._make_request('taxpayer/verify', method='GET')
            self.last_sync = fields.Datetime.now()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Successful'),
                    'message': _('Successfully connected to GRA E-VAT system.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except UserError as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Failed'),
                    'message': str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def action_register_device(self):
        """Register device with GRA E-VAT."""
        self.ensure_one()

        data = {
            'tin': self.tin,
            'branch_code': self.branch_code,
            'device_type': 'ERP',
            'timestamp': datetime.now().isoformat(),
        }

        result = self._make_request('device/register', data=data)

        if result.get('device_serial'):
            self.write({
                'device_serial': result['device_serial'],
                'is_registered': True,
                'last_sync': fields.Datetime.now(),
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Device Registered'),
                    'message': _('Device serial: %s') % result['device_serial'],
                    'type': 'success',
                    'sticky': False,
                }
            }

        raise UserError(_("Device registration failed. Please contact GRA support."))
