# -*- coding: utf-8 -*-
import json
import logging
import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

SANDBOX_URL = 'https://etims-api-sbx.kra.go.ke/etims-api'
PRODUCTION_URL = 'https://etims-api.kra.go.ke/etims-api'


class EtimsConfig(models.Model):
    _name = 'etims.config'
    _description = 'eTIMS Configuration'

    name = fields.Char(default='eTIMS Configuration', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    # Environment
    environment = fields.Selection([
        ('sandbox', 'Sandbox (Testing)'),
        ('production', 'Production'),
    ], string='Environment', default='sandbox', required=True)

    # Credentials from KRA
    tin = fields.Char(string='TIN (KRA PIN)', required=True,
                      help='Your KRA PIN e.g. P000000000X')
    bhf_id = fields.Char(string='Branch ID', default='00', required=True,
                         help='Branch ID, usually 00 for main branch')
    dvc_srl_no = fields.Char(string='Device Serial No', required=True,
                             help='Device serial number from KRA')

    # Communication key (received after device initialization)
    cmn_key = fields.Char(string='Communication Key',
                          help='Key received from KRA after device init')

    # Status
    last_request_date = fields.Datetime(string='Last Request')
    last_response = fields.Text(string='Last Response')

    _sql_constraints = [
        ('company_uniq', 'unique(company_id)',
         'Only one eTIMS configuration per company allowed.')
    ]

    def _get_api_url(self):
        """Get the API base URL based on environment."""
        self.ensure_one()
        return SANDBOX_URL if self.environment == 'sandbox' else PRODUCTION_URL

    def _prepare_headers(self):
        """Prepare HTTP headers for API request."""
        return {
            'Content-Type': 'application/json',
        }

    def _call_api(self, endpoint, data):
        """
        Make an API call to eTIMS.

        :param endpoint: API endpoint (e.g., '/trnsSales/saveSalesWr')
        :param data: Dictionary with request data
        :return: Response dictionary
        """
        self.ensure_one()
        url = self._get_api_url() + endpoint

        # Add common fields to request
        data.update({
            'tin': self.tin,
            'bhfId': self.bhf_id,
            'dvcSrlNo': self.dvc_srl_no,
        })
        if self.cmn_key:
            data['cmnKey'] = self.cmn_key

        _logger.info('eTIMS API Request to %s: %s', endpoint, json.dumps(data, indent=2))

        try:
            response = requests.post(
                url,
                json=data,
                headers=self._prepare_headers(),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            # Log response
            self.write({
                'last_request_date': fields.Datetime.now(),
                'last_response': json.dumps(result, indent=2),
            })

            _logger.info('eTIMS API Response: %s', json.dumps(result, indent=2))
            return result

        except requests.exceptions.RequestException as e:
            _logger.error('eTIMS API Error: %s', str(e))
            raise UserError(_('eTIMS API Error: %s') % str(e))

    def action_test_connection(self):
        """Test connection to eTIMS API."""
        self.ensure_one()
        try:
            # Use device verification endpoint to test
            result = self._call_api('/selectInitInfo', {})

            if result.get('resultCd') == '000':
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Connection to eTIMS successful!'),
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_('eTIMS Error: %s') % result.get('resultMsg', 'Unknown error'))
        except Exception as e:
            raise UserError(_('Connection test failed: %s') % str(e))

    @api.model
    def get_config(self, company=None):
        """Get eTIMS config for company."""
        company = company or self.env.company
        config = self.search([('company_id', '=', company.id)], limit=1)
        if not config:
            raise UserError(_(
                'eTIMS not configured for %s. Go to Invoicing > Configuration > eTIMS Configuration.'
            ) % company.name)
        return config
