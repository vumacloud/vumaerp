# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class EfrisDevice(models.Model):
    _name = 'efris.device'
    _description = 'EFRIS Device'
    _rec_name = 'device_no'

    device_no = fields.Char(
        string='Device Number',
        required=True,
        help='Device number assigned by URA',
    )
    device_id = fields.Char(
        string='Device ID',
        readonly=True,
        help='Device ID returned after registration',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    config_id = fields.Many2one(
        'efris.config',
        string='EFRIS Configuration',
        compute='_compute_config_id',
        store=True,
    )

    status = fields.Selection([
        ('inactive', 'Inactive'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
    ], string='Status', default='inactive')

    # Device Location
    branch_name = fields.Char(string='Branch Name')
    branch_code = fields.Char(string='Branch Code')
    address = fields.Text(string='Address')

    # Counters
    last_invoice_no = fields.Integer(string='Last Invoice Number', default=0)
    last_receipt_no = fields.Integer(string='Last Receipt Number', default=0)

    # Timestamps
    registration_date = fields.Date(string='Registration Date', readonly=True)
    last_activity = fields.Datetime(string='Last Activity', readonly=True)

    _sql_constraints = [
        ('device_no_company_uniq', 'unique(device_no, company_id)',
         'Device number must be unique per company!'),
    ]

    @api.depends('company_id')
    def _compute_config_id(self):
        for device in self:
            device.config_id = self.env['efris.config'].search([
                ('company_id', '=', device.company_id.id),
                ('active', '=', True),
            ], limit=1)

    def action_activate(self):
        """Activate the device."""
        self.ensure_one()
        if not self.config_id:
            raise UserError(_("No EFRIS configuration found for this company."))

        self.write({
            'status': 'active',
            'last_activity': fields.Datetime.now(),
        })

    def action_deactivate(self):
        """Deactivate the device."""
        self.ensure_one()
        self.write({
            'status': 'inactive',
            'last_activity': fields.Datetime.now(),
        })

    def get_next_invoice_number(self):
        """Get the next invoice number for this device."""
        self.ensure_one()
        self.last_invoice_no += 1
        self.last_activity = fields.Datetime.now()
        return self.last_invoice_no

    def get_next_receipt_number(self):
        """Get the next receipt number for this device."""
        self.ensure_one()
        self.last_receipt_no += 1
        self.last_activity = fields.Datetime.now()
        return self.last_receipt_no
