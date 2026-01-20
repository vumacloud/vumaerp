# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Ghana E-VAT fields
    evat_submitted = fields.Boolean(
        string='Submitted to GRA',
        default=False,
        copy=False,
    )
    evat_submission_date = fields.Datetime(
        string='E-VAT Submission Date',
        copy=False,
    )
    evat_reference = fields.Char(
        string='E-VAT Reference',
        copy=False,
        help='GRA E-VAT transaction reference number',
    )
    evat_qr_code = fields.Char(
        string='E-VAT QR Code',
        copy=False,
    )
    evat_status = fields.Selection([
        ('draft', 'Not Submitted'),
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='E-VAT Status', default='draft', copy=False)

    evat_error_message = fields.Text(
        string='E-VAT Error',
        copy=False,
    )

    # Customer/Supplier TIN
    partner_tin = fields.Char(
        related='partner_id.vat',
        string='Partner TIN',
    )

    def _prepare_evat_invoice_data(self):
        """Prepare invoice data for E-VAT submission."""
        self.ensure_one()

        if self.move_type not in ['out_invoice', 'out_refund']:
            raise UserError(_("Only customer invoices can be submitted to E-VAT."))

        if self.state != 'posted':
            raise UserError(_("Only posted invoices can be submitted to E-VAT."))

        # Prepare line items
        items = []
        for line in self.invoice_line_ids.filtered(lambda l: not l.display_type):
            item = {
                'description': line.name or line.product_id.name,
                'quantity': line.quantity,
                'unit_price': line.price_unit,
                'discount': line.discount,
                'total_amount': line.price_subtotal,
                'vat_amount': line.price_total - line.price_subtotal,
            }
            if line.product_id:
                item['item_code'] = line.product_id.default_code or ''
                item['item_description'] = line.product_id.name

            items.append(item)

        data = {
            'invoice_number': self.name,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else datetime.now().date().isoformat(),
            'invoice_type': '01' if self.move_type == 'out_invoice' else '02',
            'currency': self.currency_id.name,
            'exchange_rate': 1.0,  # TODO: Get actual exchange rate

            # Customer info
            'customer_tin': self.partner_id.vat or '',
            'customer_name': self.partner_id.name,
            'customer_address': self.partner_id.contact_address or '',

            # Amounts
            'subtotal': self.amount_untaxed,
            'total_vat': self.amount_tax,
            'total_amount': self.amount_total,

            # Items
            'items': items,
        }

        return data

    def action_submit_to_evat(self):
        """Submit invoice to GRA E-VAT."""
        self.ensure_one()

        if self.evat_submitted:
            raise UserError(_("This invoice has already been submitted to E-VAT."))

        config = self.env['ghana.evat.config'].get_config(self.company_id)

        if not config.is_registered:
            raise UserError(_("E-VAT device is not registered. Please register first."))

        # Prepare invoice data
        invoice_data = self._prepare_evat_invoice_data()

        try:
            # Submit to GRA
            result = config._make_request('invoice/submit', data=invoice_data)

            # Update invoice with response
            self.write({
                'evat_submitted': True,
                'evat_submission_date': fields.Datetime.now(),
                'evat_reference': result.get('reference_number'),
                'evat_qr_code': result.get('qr_code'),
                'evat_status': 'submitted',
                'evat_error_message': False,
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('E-VAT Submission Successful'),
                    'message': _('Reference: %s') % result.get('reference_number'),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except UserError as e:
            self.write({
                'evat_status': 'rejected',
                'evat_error_message': str(e),
            })
            raise

    def action_cancel_evat(self):
        """Cancel E-VAT submission."""
        self.ensure_one()

        if not self.evat_submitted:
            raise UserError(_("This invoice has not been submitted to E-VAT."))

        config = self.env['ghana.evat.config'].get_config(self.company_id)

        cancel_data = {
            'reference_number': self.evat_reference,
            'reason': 'Invoice cancelled',
        }

        result = config._make_request('invoice/cancel', data=cancel_data)

        self.write({
            'evat_status': 'cancelled',
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('E-VAT Cancellation'),
                'message': _('Invoice E-VAT submission has been cancelled.'),
                'type': 'warning',
                'sticky': False,
            }
        }
