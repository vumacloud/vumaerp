# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import hashlib
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # EBM Fields
    ebm_submitted = fields.Boolean(
        string='Submitted to EBM',
        default=False,
        copy=False
    )
    ebm_receipt_number = fields.Char(
        string='EBM Receipt Number',
        copy=False,
        help='Receipt number returned by RRA EBM system'
    )
    ebm_internal_data = fields.Char(
        string='EBM Internal Data',
        copy=False
    )
    ebm_receipt_signature = fields.Char(
        string='EBM Signature',
        copy=False
    )
    ebm_submission_date = fields.Datetime(
        string='EBM Submission Date',
        copy=False
    )
    ebm_invoice_type = fields.Selection([
        ('NS', 'Normal Sale'),
        ('CP', 'Copy'),
        ('TR', 'Training Invoice'),
        ('PF', 'Proforma Invoice'),
        ('CN', 'Credit Note'),
    ], string='EBM Invoice Type', default='NS')

    ebm_response = fields.Text(
        string='EBM Response',
        copy=False
    )
    ebm_qr_code = fields.Char(
        string='EBM QR Code',
        copy=False,
        help='QR code data for the receipt'
    )

    def action_post(self):
        """Override to submit to EBM after posting"""
        res = super().action_post()
        for move in self:
            if (move.move_type in ('out_invoice', 'out_refund') and
                    move.company_id.ebm_enabled and
                    not move.ebm_submitted):
                move._submit_to_ebm()
        return res

    def _submit_to_ebm(self):
        """Submit invoice to RRA EBM system"""
        self.ensure_one()
        company = self.company_id

        if not company.ebm_enabled:
            return

        if not company.ebm_device_id or not company.rra_tin:
            raise UserError(_('Please configure EBM Device ID and TIN in company settings.'))

        # Prepare invoice data
        invoice_data = self._prepare_ebm_data()

        try:
            # In production, this would call the actual RRA EBM API
            # For now, we simulate the response
            response = self._call_ebm_api(invoice_data)

            if response.get('success'):
                self.write({
                    'ebm_submitted': True,
                    'ebm_receipt_number': response.get('receipt_number'),
                    'ebm_internal_data': response.get('internal_data'),
                    'ebm_receipt_signature': response.get('signature'),
                    'ebm_submission_date': fields.Datetime.now(),
                    'ebm_response': json.dumps(response),
                    'ebm_qr_code': response.get('qr_code'),
                })
                _logger.info(f'Invoice {self.name} submitted to EBM successfully')
            else:
                raise UserError(_('EBM submission failed: %s') % response.get('error', 'Unknown error'))

        except Exception as e:
            _logger.error(f'EBM submission error for {self.name}: {str(e)}')
            raise UserError(_('Failed to submit to EBM: %s') % str(e))

    def _prepare_ebm_data(self):
        """Prepare invoice data for EBM submission"""
        self.ensure_one()

        # Calculate totals
        total_taxable = sum(line.price_subtotal for line in self.invoice_line_ids)
        total_tax = self.amount_tax
        total_amount = self.amount_total

        # Determine invoice type for credit notes
        invoice_type = self.ebm_invoice_type
        if self.move_type == 'out_refund':
            invoice_type = 'CN'

        items = []
        for line in self.invoice_line_ids:
            tax_rate = 0
            if line.tax_ids:
                tax_rate = line.tax_ids[0].amount
            items.append({
                'name': line.name or line.product_id.name,
                'quantity': line.quantity,
                'unit_price': line.price_unit,
                'tax_rate': tax_rate,
                'total': line.price_subtotal,
            })

        return {
            'tin': self.company_id.rra_tin,
            'device_id': self.company_id.ebm_device_id,
            'invoice_number': self.name,
            'invoice_type': invoice_type,
            'invoice_date': self.invoice_date.strftime('%Y-%m-%d'),
            'customer_tin': self.partner_id.vat or '',
            'customer_name': self.partner_id.name,
            'items': items,
            'total_taxable': total_taxable,
            'total_tax': total_tax,
            'total_amount': total_amount,
            'currency': self.currency_id.name,
        }

    def _call_ebm_api(self, invoice_data):
        """
        Call RRA EBM API
        In production, this would make actual HTTP requests to the RRA API
        """
        company = self.company_id

        if company.ebm_environment == 'sandbox':
            # Simulate successful response in sandbox mode
            receipt_num = f"EBM{datetime.now().strftime('%Y%m%d%H%M%S')}"
            signature = hashlib.sha256(
                f"{invoice_data['invoice_number']}{receipt_num}".encode()
            ).hexdigest()[:32]

            return {
                'success': True,
                'receipt_number': receipt_num,
                'internal_data': f"SDC:{company.ebm_device_id}",
                'signature': signature,
                'qr_code': f"https://efiling.rra.gov.rw/verify/{receipt_num}",
            }

        # Production API call would go here
        # import requests
        # response = requests.post(
        #     f"{company.ebm_api_url}/invoice",
        #     json=invoice_data,
        #     auth=(company.ebm_api_username, company.ebm_api_password)
        # )
        # return response.json()

        raise UserError(_('Production EBM integration requires RRA API credentials.'))

    def action_resubmit_ebm(self):
        """Manually resubmit to EBM"""
        for move in self:
            if move.move_type in ('out_invoice', 'out_refund'):
                move.ebm_submitted = False
                move._submit_to_ebm()
