# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EtimsDevice(models.Model):
    _name = 'etims.device'
    _description = 'eTIMS Device'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
    )
    serial_number = fields.Char(string='Serial Number', required=True)
    device_id = fields.Char(string='Device ID', readonly=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    config_id = fields.Many2one(
        'etims.config',
        string='Configuration',
        compute='_compute_config_id',
    )
    branch_id = fields.Char(string='Branch ID', size=2, default='00')

    # Device Info
    device_type = fields.Selection([
        ('oscu', 'OSCU (Online)'),
        ('vscu', 'VSCU (Virtual)'),
    ], string='Device Type', default='oscu', required=True)

    # State (using 'state' for consistency with views)
    state = fields.Selection([
        ('draft', 'Not Registered'),
        ('verified', 'Verified'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], string='State', default='draft', tracking=True)

    # Communication
    communication_key = fields.Char(string='Communication Key')
    comm_key = fields.Char(
        string='Comm Key',
        related='communication_key',
        readonly=False,
    )
    last_request_date = fields.Datetime(string='Last Request Date')
    last_receipt_number = fields.Char(string='Last Receipt Number', readonly=True)

    # SDC Information
    sdc_id = fields.Char(string='SDC ID', readonly=True)
    mrc_no = fields.Char(string='MRC Number', readonly=True)

    # Counters
    invoice_counter = fields.Integer(string='Invoice Counter', default=0)

    @api.depends('serial_number', 'device_type')
    def _compute_name(self):
        for device in self:
            device.name = f"{device.device_type.upper() if device.device_type else 'Device'} - {device.serial_number or 'New'}"

    @api.depends('company_id')
    def _compute_config_id(self):
        for device in self:
            device.config_id = self.env['etims.config'].search([
                ('company_id', '=', device.company_id.id),
                ('is_active', '=', True),
            ], limit=1)

    _sql_constraints = [
        ('serial_uniq', 'unique(serial_number, company_id)',
         'Device serial number must be unique per company.'),
    ]

    def action_verify_device(self):
        """Verify device with KRA."""
        self.ensure_one()
        config = self.env['etims.config'].get_active_config(self.company_id)
        if not config:
            raise UserError(_('No active eTIMS configuration found for this company.'))

        api = self.env['etims.api']
        try:
            result = api.device_verification(config, {
                'tin': config.tin,
                'bhfId': self.branch_id or '00',
                'dvcSrlNo': self.serial_number,
            })

            if result.get('resultCd') == '000':
                result_data = result.get('data', {})
                self.write({
                    'state': 'verified',
                    'device_id': result_data.get('sdcId'),
                    'sdc_id': result_data.get('sdcId'),
                    'last_request_date': fields.Datetime.now(),
                })
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Device verified successfully!'),
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_('Device verification failed: %s') % result.get('resultMsg'))
        except Exception as e:
            raise UserError(_('Verification error: %s') % str(e))

    def action_initialize(self):
        """Initialize device and get communication key."""
        self.ensure_one()
        if self.state != 'verified':
            raise UserError(_('Device must be verified before initialization.'))

        config = self.env['etims.config'].get_active_config(self.company_id)
        if not config:
            raise UserError(_('No active eTIMS configuration found.'))

        api = self.env['etims.api']
        try:
            result = api.device_initialization(config, {
                'tin': config.tin,
                'bhfId': self.branch_id or '00',
                'dvcSrlNo': self.serial_number,
            })

            if result.get('resultCd') == '000':
                result_data = result.get('data', {})
                comm_key = result_data.get('cmcKey')
                self.write({
                    'state': 'active',
                    'communication_key': comm_key,
                    'mrc_no': result_data.get('mrcNo'),
                    'last_request_date': fields.Datetime.now(),
                })
                # Update config with comm key
                config.write({
                    'comm_key': comm_key,
                    'device_id': self.id,
                    'device_serial': self.serial_number,
                    'status': 'active',
                })
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Device initialized! Communication key received.'),
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_('Initialization failed: %s') % result.get('resultMsg'))
        except Exception as e:
            raise UserError(_('Initialization error: %s') % str(e))

    def action_register(self):
        """Register device with KRA (legacy method)."""
        return self.action_verify_device()

    def get_next_invoice_number(self):
        """Get next invoice number for this device."""
        self.ensure_one()
        self.invoice_counter += 1
        return self.invoice_counter

    def update_last_receipt(self, receipt_number):
        """Update last receipt number."""
        self.ensure_one()
        self.write({
            'last_receipt_number': receipt_number,
            'last_request_date': fields.Datetime.now(),
        })
