# -*- coding: utf-8 -*-
import json
import logging
import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

SANDBOX_URL = 'https://apitest.e-vatgh.com/evat_apiqa'
PRODUCTION_URL = 'https://api.e-vatgh.com/evat_api'


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

    # GRA Credentials
    tin = fields.Char(string='TIN', required=True,
                      help='GRA Tax Identification Number (e.g., C00XXXXXXXX)')
    company_name = fields.Char(string='Company Name (GRA)', required=True,
                               help='Company name as registered with GRA')
    security_key = fields.Char(string='Security Key', required=True,
                               help='E-VAT API Security Key from GRA')

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

    def _prepare_headers(self):
        """Prepare HTTP headers for API request."""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _call_api(self, endpoint, data):
        """
        Make an API call to GRA E-VAT.

        :param endpoint: API endpoint (e.g., 'post_receipt_Json.jsp')
        :param data: Dictionary with request data
        :return: Response dictionary
        """
        self.ensure_one()
        url = f"{self._get_api_url()}/{endpoint}"

        # Add authentication to payload
        data.update({
            'COMPANY_TIN': self.tin,
            'COMPANY_NAMES': self.company_name,
            'COMPANY_SECURITY_KEY': self.security_key,
        })

        _logger.info('GRA E-VAT API Request to %s', url)

        try:
            response = requests.post(
                url,
                json=data,
                headers=self._prepare_headers(),
                timeout=30
            )

            # Log response
            self.write({
                'last_request_date': fields.Datetime.now(),
                'last_response': response.text[:5000] if response.text else '',
            })

            if response.status_code == 200:
                result = response.json()
                _logger.info('GRA E-VAT API Response: %s', json.dumps(result, indent=2))
                return result
            else:
                raise UserError(_('E-VAT API Error %s: %s') % (response.status_code, response.text))

        except requests.exceptions.Timeout:
            raise UserError(_('Connection to GRA E-VAT timed out.'))
        except requests.exceptions.ConnectionError as e:
            raise UserError(_('Cannot connect to GRA E-VAT: %s') % str(e))
        except json.JSONDecodeError:
            raise UserError(_('Invalid response from GRA E-VAT server.'))

    def action_test_connection(self):
        """Test connection to GRA E-VAT API."""
        self.ensure_one()
        try:
            url = f"{self._get_api_url()}/get_Response_JSON.jsp"
            response = requests.post(
                url,
                json={
                    'COMPANY_TIN': self.tin,
                    'COMPANY_NAMES': self.company_name,
                    'COMPANY_SECURITY_KEY': self.security_key,
                },
                headers=self._prepare_headers(),
                timeout=30
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
                        'title': _('Success'),
                        'message': _('Connection to GRA E-VAT successful!'),
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_('E-VAT Error: %s') % response.text[:200])
        except Exception as e:
            raise UserError(_('Connection test failed: %s') % str(e))

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
