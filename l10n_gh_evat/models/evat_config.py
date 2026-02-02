# Part of VumaERP. See LICENSE file for full copyright and licensing details.

import hashlib
import json
import logging
import requests
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# GRA E-VAT API Endpoints
# Reference: https://gra.gov.gh/e-services/e-vat/
EVAT_SANDBOX_URL = "https://apitest.e-vatgh.com/evat_apiqa"
EVAT_PRODUCTION_URL = "https://api.e-vatgh.com/evat_api"


class GhanaEvatConfig(models.Model):
    _name = 'ghana.evat.config'
    _description = 'Ghana E-VAT Configuration'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    environment = fields.Selection([
        ('sandbox', 'Sandbox (Testing)'),
        ('production', 'Production'),
    ], string='Environment', default='sandbox', required=True)

    # GRA Credentials
    # Reference: GRA E-VAT API Documentation
    tin = fields.Char(
        string='TIN',
        help='Ghana Revenue Authority Tax Identification Number (e.g., C00XXXXXXXX)',
    )
    company_name = fields.Char(
        string='Company Name (GRA)',
        help='Company name as registered with GRA for E-VAT',
    )
    security_key = fields.Char(
        string='Security Key',
        help='E-VAT API Security Key provided by GRA',
    )

    # Status tracking
    last_request_date = fields.Datetime(
        string='Last Request Date',
        readonly=True,
    )
    last_response = fields.Text(
        string='Last Response',
        readonly=True,
    )

    api_url = fields.Char(
        string='API URL',
        compute='_compute_api_url',
    )

    _sql_constraints = [
        ('company_unique', 'unique(company_id)',
         'Only one E-VAT configuration per company is allowed.'),
    ]

    @api.depends('environment')
    def _compute_api_url(self):
        """Compute API URL based on environment selection."""
        for record in self:
            if record.environment == 'production':
                record.api_url = EVAT_PRODUCTION_URL
            else:
                record.api_url = EVAT_SANDBOX_URL

    def _get_headers(self):
        """
        Prepare HTTP headers for GRA E-VAT API requests.

        Returns:
            dict: HTTP headers including authentication
        """
        self.ensure_one()
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _prepare_auth_payload(self):
        """
        Prepare authentication payload for GRA E-VAT API.

        Based on GRA E-VAT API documentation:
        - COMPANY_TIN: Tax Identification Number
        - COMPANY_NAMES: Registered company name
        - COMPANY_SECURITY_KEY: API security key

        Returns:
            dict: Authentication fields for API payload
        """
        self.ensure_one()
        if not self.tin or not self.company_name or not self.security_key:
            raise UserError(_('Please configure TIN, Company Name, and Security Key.'))

        return {
            'COMPANY_TIN': self.tin,
            'COMPANY_NAMES': self.company_name,
            'COMPANY_SECURITY_KEY': self.security_key,
        }

    def _call_api(self, endpoint, data):
        """
        Make API call to GRA E-VAT system.

        Args:
            endpoint: API endpoint path (e.g., 'post_receipt_Json.jsp')
            data: Dictionary payload to send

        Returns:
            dict: Parsed JSON response

        Raises:
            UserError: On API errors or connection failures
        """
        self.ensure_one()
        url = f"{self.api_url}/{endpoint}"
        headers = self._get_headers()

        # Add authentication to payload
        payload = {**self._prepare_auth_payload(), **data}

        _logger.info("GRA E-VAT API Request to %s", url)
        _logger.debug("Payload: %s", json.dumps(payload, indent=2))

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30,
            )

            # Update tracking fields
            self.write({
                'last_request_date': fields.Datetime.now(),
                'last_response': response.text[:5000] if response.text else '',
            })

            if response.status_code == 200:
                result = response.json()
                _logger.info("GRA E-VAT API Response: %s", result)
                return result
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                _logger.error(error_msg)
                raise UserError(_(error_msg))

        except requests.exceptions.Timeout:
            raise UserError(_('Connection to GRA E-VAT timed out. Please try again.'))
        except requests.exceptions.ConnectionError as e:
            raise UserError(_('Cannot connect to GRA E-VAT: %s') % str(e))
        except json.JSONDecodeError:
            raise UserError(_('Invalid response from GRA E-VAT server.'))

    def action_test_connection(self):
        """
        Test connection to GRA E-VAT API.

        Returns:
            dict: Notification action with result
        """
        self.ensure_one()

        if not self.tin or not self.security_key:
            raise UserError(_('Please configure TIN and Security Key first.'))

        # For connection test, we attempt a minimal API call
        # The actual endpoint may vary based on GRA API version
        try:
            # Attempt to get response endpoint which validates credentials
            url = f"{self.api_url}/get_Response_JSON.jsp"
            headers = self._get_headers()
            payload = self._prepare_auth_payload()

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30,
            )

            self.write({
                'last_request_date': fields.Datetime.now(),
                'last_response': response.text[:5000] if response.text else '',
            })

            if response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Successful'),
                        'message': _('Successfully connected to GRA E-VAT (%s)') % self.environment,
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Failed'),
                        'message': _('Error %s: %s') % (response.status_code, response.text[:200]),
                        'type': 'danger',
                        'sticky': True,
                    }
                }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Error'),
                    'message': str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }

    @api.model
    def get_config(self, company=None):
        """
        Get E-VAT configuration for a company.

        Args:
            company: res.company record or None for current company

        Returns:
            ghana.evat.config record or raises UserError
        """
        if company is None:
            company = self.env.company

        config = self.search([('company_id', '=', company.id)], limit=1)
        if not config:
            raise UserError(_(
                'E-VAT is not configured for company %s. '
                'Please go to Invoicing > Configuration > Ghana E-VAT Configuration.'
            ) % company.name)
        return config
