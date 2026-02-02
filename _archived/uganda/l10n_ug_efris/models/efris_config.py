# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import requests
import json
import logging
import hashlib
import base64
from datetime import datetime

_logger = logging.getLogger(__name__)

# EFRIS API Endpoints
EFRIS_SANDBOX_URL = "https://efristest.ura.go.ug/efrisws/ws"
EFRIS_PRODUCTION_URL = "https://efris.ura.go.ug/efrisws/ws"


class EfrisConfig(models.Model):
    _name = 'efris.config'
    _description = 'EFRIS Configuration'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)

    # URA Credentials
    tin = fields.Char(
        string='TIN',
        required=True,
        help='Taxpayer Identification Number registered with URA',
    )
    device_no = fields.Char(
        string='Device Number',
        required=True,
        help='EFRIS Device Number assigned by URA',
    )

    # Environment
    environment = fields.Selection([
        ('sandbox', 'Sandbox (Testing)'),
        ('production', 'Production'),
    ], string='Environment', default='sandbox', required=True)

    # API Credentials
    private_key = fields.Text(
        string='Private Key',
        help='Private key for signing requests',
    )
    public_key = fields.Text(
        string='Public Key',
        help='Public key for encryption',
    )

    # Device Status
    device_id = fields.Char(string='Device ID', readonly=True)
    device_status = fields.Selection([
        ('unregistered', 'Unregistered'),
        ('registered', 'Registered'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
    ], string='Device Status', default='unregistered', readonly=True)
    last_sync = fields.Datetime(string='Last Sync', readonly=True)

    # Counters
    invoice_sequence = fields.Integer(string='Invoice Sequence', default=0)

    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one EFRIS configuration per company is allowed!'),
    ]

    @property
    def api_url(self):
        """Return the appropriate API URL based on environment."""
        if self.environment == 'production':
            return EFRIS_PRODUCTION_URL
        return EFRIS_SANDBOX_URL

    def _get_headers(self):
        """Return standard headers for EFRIS API requests."""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _build_request_data(self, interface_code, content):
        """Build the standard EFRIS request wrapper."""
        return {
            "data": {
                "content": base64.b64encode(json.dumps(content).encode()).decode(),
                "signature": "",
                "dataDescription": {
                    "codeType": "0",
                    "encryptCode": "1",
                    "zipCode": "0"
                }
            },
            "globalInfo": {
                "appId": "AP04",
                "version": "1.1.20191201",
                "dataExchangeId": self._generate_exchange_id(),
                "interfaceCode": interface_code,
                "requestCode": "TP",
                "requestTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "responseCode": "TA",
                "userName": self.tin,
                "deviceMAC": "",
                "deviceNo": self.device_no,
                "tin": self.tin,
                "brn": "",
                "taxpayerID": "",
                "longitude": "32.5825",
                "latitude": "0.3476",
                "agentType": "0",
                "extendField": {
                    "responseDateFormat": "dd/MM/yyyy",
                    "responseTimeFormat": "dd/MM/yyyy HH:mm:ss"
                }
            },
            "returnStateInfo": {
                "returnCode": "",
                "returnMessage": ""
            }
        }

    def _generate_exchange_id(self):
        """Generate unique data exchange ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{self.tin}{self.device_no}{timestamp}"

    def _send_request(self, interface_code, content):
        """Send request to EFRIS API."""
        self.ensure_one()

        url = self.api_url
        headers = self._get_headers()
        data = self._build_request_data(interface_code, content)

        _logger.info(f"EFRIS Request to {interface_code}: {json.dumps(data)}")

        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            _logger.info(f"EFRIS Response: {json.dumps(result)}")

            return_state = result.get('returnStateInfo', {})
            if return_state.get('returnCode') != '00':
                raise UserError(_(
                    "EFRIS Error: %s - %s"
                ) % (return_state.get('returnCode'), return_state.get('returnMessage')))

            return result

        except requests.exceptions.RequestException as e:
            _logger.error(f"EFRIS API Error: {str(e)}")
            raise UserError(_("EFRIS Connection Error: %s") % str(e))

    def action_test_connection(self):
        """Test connection to EFRIS API."""
        self.ensure_one()

        # Query taxpayer information to test connection
        content = {
            "tin": self.tin,
            "ninBrn": "",
        }

        try:
            result = self._send_request("T119", content)
            self.write({
                'device_status': 'active',
                'last_sync': fields.Datetime.now(),
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Successfully connected to EFRIS API'),
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
        """Register device with EFRIS."""
        self.ensure_one()

        content = {
            "deviceNo": self.device_no,
            "tin": self.tin,
        }

        result = self._send_request("T101", content)

        # Parse response
        data = result.get('data', {})
        if data.get('content'):
            response_content = json.loads(
                base64.b64decode(data['content']).decode()
            )
            self.write({
                'device_id': response_content.get('deviceId'),
                'device_status': 'registered',
                'last_sync': fields.Datetime.now(),
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Device registered successfully'),
                'type': 'success',
                'sticky': False,
            }
        }

    def get_next_invoice_number(self):
        """Get the next invoice sequence number."""
        self.ensure_one()
        self.invoice_sequence += 1
        return self.invoice_sequence
