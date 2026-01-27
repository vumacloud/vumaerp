# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import re
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Kenya-specific fields
    etims_pin = fields.Char(
        string='KRA PIN',
        size=11,
        help='Kenya Revenue Authority Personal Identification Number',
    )
    etims_pin_validated = fields.Boolean(
        string='PIN Validated',
        default=False,
        copy=False,
    )
    etims_pin_validation_date = fields.Datetime(
        string='PIN Validation Date',
        copy=False,
        readonly=True,
    )
    etims_customer_type = fields.Selection([
        ('local', 'Local Customer'),
        ('export', 'Export Customer'),
        ('exempt', 'Exempt Organization'),
    ], string='Customer Type', default='local')

    etims_branch_id = fields.Char(
        string='eTIMS Branch ID',
        help='Customer branch ID for eTIMS',
    )

    @api.constrains('etims_pin')
    def _check_etims_pin(self):
        """Validate KRA PIN format."""
        pin_pattern = re.compile(r'^[AP]\d{9}[A-Z]$')
        for partner in self:
            if partner.etims_pin:
                if not pin_pattern.match(partner.etims_pin):
                    raise ValidationError(_(
                        'Invalid KRA PIN format. PIN must be in format: '
                        'A/P + 9 digits + letter (e.g., A123456789B or P987654321X)'
                    ))

    @api.onchange('etims_pin')
    def _onchange_etims_pin(self):
        """Reset validation when PIN changes."""
        if self.etims_pin:
            self.etims_pin = self.etims_pin.upper()
        self.etims_pin_validated = False

    def action_validate_pin(self):
        """Validate customer PIN with KRA eTIMS."""
        self.ensure_one()

        if not self.etims_pin:
            raise UserError(_('Please enter a KRA PIN first.'))

        config = self.env['etims.config'].get_active_config()
        if not config:
            raise UserError(_('eTIMS is not configured. Please configure eTIMS settings first.'))

        api = self.env['etims.api']

        try:
            response = api.search_customer(config, {
                'tin': config.tin,
                'bhfId': config.branch_id or '00',
                'custmTin': self.etims_pin,
            })

            if response.get('resultCd') == '000':
                customer_data = response.get('data', {})
                if customer_data:
                    # Update partner with validated info
                    update_vals = {
                        'etims_pin_validated': True,
                        'etims_pin_validation_date': fields.Datetime.now(),
                    }

                    # Update name if available and partner name is not set
                    if customer_data.get('custNm') and not self.name:
                        update_vals['name'] = customer_data.get('custNm')

                    self.write(update_vals)

                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('PIN Validated'),
                            'message': _('KRA PIN validated successfully.'),
                            'type': 'success',
                        }
                    }
                else:
                    raise UserError(_('PIN not found in KRA database.'))
            else:
                error_msg = response.get('resultMsg', 'Unknown error')
                raise UserError(_('KRA Validation Error: %s') % error_msg)

        except Exception as e:
            _logger.error('PIN validation error: %s', str(e))
            raise UserError(_('Failed to validate PIN: %s') % str(e))

    def action_search_kra(self):
        """Search for customer in KRA database."""
        self.ensure_one()

        if not self.etims_pin:
            raise UserError(_('Please enter a KRA PIN to search.'))

        config = self.env['etims.config'].get_active_config()
        if not config:
            raise UserError(_('eTIMS is not configured.'))

        api = self.env['etims.api']

        try:
            response = api.search_customer(config, {
                'tin': config.tin,
                'bhfId': config.branch_id or '00',
                'custmTin': self.etims_pin,
            })

            if response.get('resultCd') == '000':
                data = response.get('data', {})
                if data:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': _('KRA Customer Info'),
                        'res_model': 'etims.customer.info.wizard',
                        'view_mode': 'form',
                        'target': 'new',
                        'context': {
                            'default_partner_id': self.id,
                            'default_customer_name': data.get('custNm', ''),
                            'default_customer_tin': data.get('custTin', ''),
                            'default_customer_status': data.get('custSttsCd', ''),
                        }
                    }
                else:
                    raise UserError(_('Customer not found in KRA database.'))
            else:
                raise UserError(_('KRA Error: %s') % response.get('resultMsg', 'Unknown error'))

        except Exception as e:
            raise UserError(_('Search failed: %s') % str(e))

    @api.model
    def create(self, vals):
        """Uppercase PIN on create."""
        if vals.get('etims_pin'):
            vals['etims_pin'] = vals['etims_pin'].upper()
        return super().create(vals)

    def write(self, vals):
        """Uppercase PIN on write."""
        if vals.get('etims_pin'):
            vals['etims_pin'] = vals['etims_pin'].upper()
            # Reset validation if PIN changes
            if 'etims_pin_validated' not in vals:
                vals['etims_pin_validated'] = False
        return super().write(vals)
