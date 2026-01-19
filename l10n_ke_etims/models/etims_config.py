# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class EtimsConfig(models.Model):
    _name = 'etims.config'
    _description = 'eTIMS Configuration'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        ondelete='cascade',
    )
    active = fields.Boolean(default=True)

    # Environment
    environment = fields.Selection([
        ('sandbox', 'Sandbox (Testing)'),
        ('production', 'Production'),
    ], string='Environment', default='sandbox', required=True)

    # API URLs
    sandbox_url = fields.Char(
        string='Sandbox URL',
        default='https://etims-api-sbx.kra.go.ke',
    )
    production_url = fields.Char(
        string='Production URL',
        default='https://etims-api.kra.go.ke/etims-api',
    )

    # Device Information
    device_id = fields.Many2one(
        'etims.device',
        string='Active Device',
    )
    branch_id = fields.Char(string='Branch ID', size=2, default='00')

    # Credentials
    tin = fields.Char(string='TIN (PIN)', size=11, required=True)
    device_serial = fields.Char(string='Device Serial Number')

    # Communication Key (from KRA after device initialization)
    comm_key = fields.Char(string='Communication Key')

    # Submission Settings
    auto_submit_invoices = fields.Boolean(
        string='Auto-submit Invoices',
        default=False,
        help='Automatically submit invoices to eTIMS on validation',
    )
    submit_on_post = fields.Boolean(
        string='Submit on Post',
        default=True,
        help='Submit invoice to eTIMS when posted',
    )

    # Status
    last_sync = fields.Datetime(string='Last Sync')
    status = fields.Selection([
        ('draft', 'Not Configured'),
        ('pending', 'Pending Verification'),
        ('active', 'Active'),
        ('error', 'Error'),
    ], string='Status', default='draft')
    status_message = fields.Text(string='Status Message')

    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one eTIMS configuration per company is allowed.'),
    ]

    @api.model
    def get_config(self, company=None):
        """Get eTIMS configuration for the given company."""
        company = company or self.env.company
        config = self.search([('company_id', '=', company.id)], limit=1)
        if not config:
            raise UserError(_('eTIMS is not configured for company %s. Please configure it first.') % company.name)
        return config

    def get_api_url(self):
        """Get the API URL based on environment."""
        self.ensure_one()
        if self.environment == 'sandbox':
            return self.sandbox_url
        return self.production_url

    def action_test_connection(self):
        """Test the connection to eTIMS API."""
        self.ensure_one()
        api = self.env['etims.api']
        try:
            result = api.device_verification(self)
            if result.get('resultCd') == '000':
                self.write({
                    'status': 'active',
                    'status_message': 'Connection successful',
                    'last_sync': fields.Datetime.now(),
                })
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
                self.write({
                    'status': 'error',
                    'status_message': result.get('resultMsg', 'Unknown error'),
                })
                raise UserError(_('eTIMS Error: %s') % result.get('resultMsg'))
        except Exception as e:
            self.write({
                'status': 'error',
                'status_message': str(e),
            })
            raise UserError(_('Connection failed: %s') % str(e))

    def action_sync_codes(self):
        """Sync all code tables from eTIMS."""
        self.ensure_one()
        api = self.env['etims.api']
        code_model = self.env['etims.code']

        code_types = [
            ('01', 'Item Classification'),
            ('02', 'Taxation Type'),
            ('03', 'Country'),
            ('04', 'Packaging Unit'),
            ('05', 'Quantity Unit'),
            ('06', 'Payment Type'),
            ('07', 'Transaction Type'),
            ('08', 'Stock Movement Type'),
            ('09', 'Product Type'),
            ('10', 'Import Status'),
        ]

        synced = 0
        for code_type, name in code_types:
            try:
                result = api.code_search(self, code_type)
                if result.get('resultCd') == '000':
                    for item in result.get('data', {}).get('itemList', []):
                        code_model.create_or_update({
                            'code_type': code_type,
                            'code': item.get('cd'),
                            'name': item.get('cdNm'),
                        })
                    synced += 1
            except Exception:
                continue

        self.last_sync = fields.Datetime.now()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sync Complete'),
                'message': _('Synced %d code tables from eTIMS.') % synced,
                'type': 'success',
            }
        }
