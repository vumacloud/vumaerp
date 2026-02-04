# -*- coding: utf-8 -*-
import json
import logging
import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# GRA E-VAT API v8.2 URLs
SANDBOX_URL = 'https://vsdcstaging.vat-gh.com'
PRODUCTION_URL = 'https://vsdc.vat-gh.com'


class GhanaEvatConfig(models.Model):
    _name = 'ghana.evat.config'
    _description = 'Ghana E-VAT Configuration'

    name = fields.Char(default='E-VAT Configuration', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    # Environment
    environment = fields.Selection([
        ('sandbox', 'Sandbox (Testing)'),
        ('production', 'Production'),
    ], string='Environment', default='sandbox', required=True)

    # GRA Credentials (v8.2)
    tin = fields.Char(string='TIN', required=True,
                      help='GRA Tax Identification Number (e.g., CXX000000YY)')
    branch_id = fields.Char(string='Branch ID', default='001',
                            help='Branch ID suffix (default: 001)')
    security_key = fields.Char(string='Security Key', required=True,
                               help='E-VAT API Security Key from GRA')
    user_name = fields.Char(string='User Name', required=True,
                            help='User name for E-VAT submissions')

    # Status
    last_request_date = fields.Datetime(string='Last Request')
    last_response = fields.Text(string='Last Response')

    _sql_constraints = [
        ('company_uniq', 'unique(company_id)',
         'Only one E-VAT configuration per company allowed.')
    ]

    def _get_api_url(self):
        """Get the API base URL based on environment."""
        self.ensure_one()
        return SANDBOX_URL if self.environment == 'sandbox' else PRODUCTION_URL

    def _get_taxpayer_endpoint(self):
        """Get the taxpayer-specific endpoint."""
        self.ensure_one()
        return f"{self._get_api_url()}/vsdc/api/v1/taxpayer/{self.tin}-{self.branch_id}"

    def _prepare_headers(self):
        """Prepare HTTP headers for API request (v8.2)."""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'security_key': self.security_key,
        }

    def _call_api(self, endpoint, data, method='POST'):
        """
        Make an API call to GRA E-VAT v8.2.

        :param endpoint: API endpoint (e.g., 'invoice')
        :param data: Dictionary with request data
        :param method: HTTP method (POST, GET)
        :return: Response dictionary
        """
        self.ensure_one()
        url = f"{self._get_taxpayer_endpoint()}/{endpoint}"

        _logger.info('GRA E-VAT API v8.2 Request to %s', url)
        _logger.debug('Request data: %s', json.dumps(data, indent=2))

        try:
            if method == 'POST':
                response = requests.post(
                    url,
                    json=data,
                    headers=self._prepare_headers(),
                    timeout=30
                )
            else:
                response = requests.get(
                    url,
                    headers=self._prepare_headers(),
                    timeout=30
                )

            # Log response
            self.write({
                'last_request_date': fields.Datetime.now(),
                'last_response': response.text[:5000] if response.text else '',
            })

            _logger.info('GRA E-VAT API Response Status: %s', response.status_code)
            _logger.debug('Response: %s', response.text[:1000])

            if response.status_code in (200, 201):
                result = response.json()
                return result
            else:
                error_msg = response.text[:500] if response.text else f'HTTP {response.status_code}'
                raise UserError(_('E-VAT API Error: %s') % error_msg)

        except requests.exceptions.Timeout:
            raise UserError(_('Connection to GRA E-VAT timed out.'))
        except requests.exceptions.ConnectionError as e:
            raise UserError(_('Cannot connect to GRA E-VAT: %s') % str(e))
        except json.JSONDecodeError:
            raise UserError(_('Invalid response from GRA E-VAT server.'))

    def action_test_connection(self):
        """Test connection to GRA E-VAT API v8.2 using health endpoint."""
        self.ensure_one()
        try:
            # Use the documented /health endpoint
            url = f"{self._get_taxpayer_endpoint()}/health"
            response = requests.get(
                url,
                headers=self._prepare_headers(),
                timeout=30
            )

            self.write({
                'last_request_date': fields.Datetime.now(),
                'last_response': response.text[:5000] if response.text else '',
            })

            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'UP':
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Connection Test'),
                            'message': _('GRA E-VAT connection successful! Status: UP'),
                            'type': 'success',
                        }
                    }
            elif response.status_code == 403:
                raise UserError(_('Invalid security key or taxpayer reference (E907).'))

            raise UserError(_('E-VAT Error: %s') % response.text[:200])
        except requests.exceptions.RequestException as e:
            raise UserError(_('Connection test failed: %s') % str(e))

    def validate_tin(self, tin):
        """
        Validate a TIN using GRA E-VAT API v8.2.
        Returns dict with tin, type, name, sector, address or raises error.
        """
        self.ensure_one()
        try:
            url = f"{self._get_taxpayer_endpoint()}/identification/tin/{tin}"
            response = requests.get(
                url,
                headers=self._prepare_headers(),
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'SUCCESS':
                    return result.get('data', {})
            raise UserError(_('TIN validation failed: %s') % response.text[:200])
        except requests.exceptions.RequestException as e:
            raise UserError(_('TIN validation error: %s') % str(e))

    @api.model
    def get_config(self, company=None):
        """Get E-VAT config for company."""
        company = company or self.env.company
        config = self.search([('company_id', '=', company.id)], limit=1)
        if not config:
            raise UserError(_(
                'E-VAT not configured for %s. Go to Invoicing > Configuration > Ghana E-VAT.'
            ) % company.name)
        return config
