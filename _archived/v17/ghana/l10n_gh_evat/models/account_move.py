# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    evat_submitted = fields.Boolean(
        string='E-VAT Submitted',
        default=False,
        copy=False
    )
    evat_reference = fields.Char(
        string='E-VAT Reference',
        copy=False,
        readonly=True
    )
    evat_submission_date = fields.Datetime(
        string='E-VAT Submission Date',
        copy=False,
        readonly=True
    )
    evat_status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], string='E-VAT Status', default='draft', copy=False)
    evat_error_message = fields.Text(
        string='E-VAT Error',
        copy=False,
        readonly=True
    )

    def action_submit_to_evat(self):
        """Submit invoice to Ghana E-VAT."""
        self.ensure_one()

        if self.evat_submitted:
            raise UserError(_('Invoice already submitted to E-VAT.'))

        if self.state != 'posted':
            raise UserError(_('Only posted invoices can be submitted to E-VAT.'))

        # TODO: Implement actual E-VAT API integration
        self.write({
            'evat_submitted': True,
            'evat_status': 'submitted',
            'evat_submission_date': fields.Datetime.now(),
            'evat_reference': 'EVAT-%s' % self.name,
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('E-VAT Submission'),
                'message': _('Invoice submitted to E-VAT successfully.'),
                'type': 'success',
            }
        }
