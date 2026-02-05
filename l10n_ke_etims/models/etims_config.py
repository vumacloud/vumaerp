# -*- coding: utf-8 -*-
import json
import logging
import re
import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# ============================================================================
# VumaERP TIS (Trader Invoicing System) Constants for KRA eTIMS
# ============================================================================
# These constants identify VumaERP to the Kenya Revenue Authority (KRA) eTIMS
# system. They must be transmitted with all eTIMS API requests.
#
# TIS Name: Registered name of the Trader Invoicing System with KRA
# TIS Version: Version number reported to KRA (TIS_MAJOR.TIS_MINOR.TIS_PATCH)
# Serial Prefix: Prefix for auto-generated device serial numbers
# ============================================================================

TIS_NAME = 'VumaERP'
TIS_VERSION = '2.0.0'  # TIS version reported to KRA (independent of Odoo version)
TIS_SERIAL_PREFIX = 'VUMAERP'  # Prefix for device serial number generation

# API Endpoints
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
    dvc_srl_no = fields.Char(
        string='Device Serial No',
        compute='_compute_dvc_srl_no',
        store=True,
        readonly=False,
        help='Device serial number. Auto-generated as VUMAERP{TIN}{SEQ} or enter manually.')

    # Communication key (received after device initialization)
    cmn_key = fields.Char(string='Communication Key',
                          help='Key received from KRA after device init')

    # TIS Information (read-only, for display)
    tis_name = fields.Char(
        string='TIS Name',
        compute='_compute_tis_info',
        store=False,
        help='Trader Invoicing System name registered with KRA')
    tis_version = fields.Char(
        string='TIS Version',
        compute='_compute_tis_info',
        store=False,
        help='TIS version number reported to KRA')

    # Status
    last_request_date = fields.Datetime(string='Last Request')
    last_response = fields.Text(string='Last Response')

    _sql_constraints = [
        ('company_uniq', 'unique(company_id)',
         'Only one eTIMS configuration per company allowed.')
    ]

    @api.depends('tin', 'bhf_id')
    def _compute_dvc_srl_no(self):
        """
        Auto-generate device serial number following VumaERP convention.

        Format: VUMAERP{TIN}{BRANCH_SEQ}
        Example: VUMAERPP051234567A00 (for branch 00)
                 VUMAERPP051234567A01 (for branch 01)

        The serial number uniquely identifies each device/branch combination
        for a company in the KRA eTIMS system.
        """
        for record in self:
            # Only auto-generate if not already set
            if record.dvc_srl_no:
                continue
            if record.tin:
                # Clean TIN: remove spaces and ensure uppercase
                clean_tin = re.sub(r'\s+', '', record.tin or '').upper()
                # Branch ID (default to '00' if not set)
                branch = record.bhf_id or '00'
                # Generate: VUMAERP + TIN + BRANCH_ID
                record.dvc_srl_no = f"{TIS_SERIAL_PREFIX}{clean_tin}{branch}"
            else:
                record.dvc_srl_no = False

    def _compute_tis_info(self):
        """Compute TIS information fields from constants."""
        for record in self:
            record.tis_name = TIS_NAME
            record.tis_version = TIS_VERSION

    @api.model
    def get_tis_info(self):
        """
        Get TIS (Trader Invoicing System) identification info.

        Returns a dict with TIS name, version, and serial prefix
        for KRA eTIMS registration and API communication.
        """
        return {
            'tis_name': TIS_NAME,
            'tis_version': TIS_VERSION,
            'tis_serial_prefix': TIS_SERIAL_PREFIX,
        }

    @api.model
    def generate_serial_number(self, tin, branch_id='00'):
        """
        Generate a device serial number following VumaERP convention.

        Args:
            tin: Company TIN/KRA PIN (e.g., 'P051234567A')
            branch_id: Branch ID (default '00' for main branch)

        Returns:
            Serial number string (e.g., 'VUMAERPP051234567A00')
        """
        clean_tin = re.sub(r'\s+', '', tin or '').upper()
        return f"{TIS_SERIAL_PREFIX}{clean_tin}{branch_id}"

    def _get_api_url(self):
        """Get the API base URL based on environment."""
        self.ensure_one()
        return SANDBOX_URL if self.environment == 'sandbox' else PRODUCTION_URL

    def _prepare_headers(self):
        """
        Prepare HTTP headers for API request.

        Includes TIS identification headers for KRA eTIMS:
        - X-TIS-Name: Trader Invoicing System name (VumaERP)
        - X-TIS-Version: TIS version number
        """
        return {
            'Content-Type': 'application/json',
            'X-TIS-Name': TIS_NAME,
            'X-TIS-Version': TIS_VERSION,
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
            # TIS identification for KRA
            'tisNm': TIS_NAME,
            'tisVersion': TIS_VERSION,
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
