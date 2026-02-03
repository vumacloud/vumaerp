# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # E-VAT Fields
    evat_submitted = fields.Boolean(string='Submitted to E-VAT', copy=False)
    evat_sdc_id = fields.Char(string='SDC ID', copy=False, readonly=True)
    evat_sdc_time = fields.Char(string='SDC Time', copy=False, readonly=True)
    evat_invoice_number = fields.Char(string='E-VAT Invoice No', copy=False, readonly=True)
    evat_internal_data = fields.Char(string='Internal Data', copy=False, readonly=True)
    evat_signature = fields.Char(string='Signature', copy=False, readonly=True)
    evat_qrcode_url = fields.Char(string='QR Code URL', copy=False, readonly=True)
    evat_submit_date = fields.Datetime(string='E-VAT Submit Date', copy=False, readonly=True)
    evat_response = fields.Text(string='E-VAT Response', copy=False, readonly=True)

    def _get_evat_date(self, dt=None):
        """Format date for GRA E-VAT: YYYY-MM-DD"""
        dt = dt or self.invoice_date or fields.Date.today()
        if isinstance(dt, str):
            dt = fields.Date.from_string(dt)
        return dt.strftime('%Y-%m-%d')

    def _get_evat_datetime(self, dt=None):
        """Format datetime for GRA E-VAT: YYYY-MM-DD HH:MM:SS"""
        dt = dt or datetime.now()
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def _get_evat_tax_code(self, tax):
        """Map Odoo tax to GRA tax code."""
        TaxCode = self.env['ghana.evat.tax.code']
        return TaxCode.map_odoo_tax_to_gra(tax)

    def _prepare_evat_item(self, line, seq):
        """Prepare a single invoice line for GRA E-VAT."""
        tax = line.tax_ids[:1] if line.tax_ids else None
        tax_code = self._get_evat_tax_code(tax)

        TaxCode = self.env['ghana.evat.tax.code']
        tax_rate = TaxCode.get_tax_rate(tax_code)

        base_amt = line.price_subtotal
        tax_amt = round(base_amt * tax_rate, 2)

        # Calculate levies for standard taxable (TAX_B)
        levy_a = levy_b = levy_d = 0.0
        if tax_code == 'TAX_B':
            levy_a = round(base_amt * 0.025, 2)  # NHIL 2.5%
            levy_b = round(base_amt * 0.025, 2)  # GETFund 2.5%

        return {
            'ITEM_SEQ': seq,
            'ITEM_CODE': line.product_id.default_code or str(line.product_id.id) if line.product_id else 'ITEM',
            'ITEM_DESC': (line.name or line.product_id.name or 'Item')[:100],
            'UNIT_PRICE': round(line.price_unit, 2),
            'QUANTITY': round(line.quantity, 3),
            'DISCOUNT_AMT': round((line.price_unit * line.quantity) - base_amt, 2),
            'TAX_CODE': tax_code,
            'TAX_RATE': round(tax_rate * 100, 2),
            'TAX_AMT': tax_amt,
            'LEVY_A_AMT': levy_a,
            'LEVY_B_AMT': levy_b,
            'LEVY_D_AMT': levy_d,
            'TOTAL_AMT': round(base_amt + tax_amt + levy_a + levy_b + levy_d, 2),
        }

    def _prepare_evat_payload(self):
        """Prepare the full GRA E-VAT payload."""
        self.ensure_one()

        if self.move_type not in ('out_invoice', 'out_refund'):
            raise UserError(_('Only customer invoices can be submitted to E-VAT.'))

        items = []
        totals = {'TAX_A': 0, 'TAX_B': 0, 'TAX_C': 0, 'TAX_D': 0, 'TAX_E': 0}
        tax_totals = {'TAX_A': 0, 'TAX_B': 0, 'TAX_C': 0, 'TAX_D': 0, 'TAX_E': 0}
        levy_a_total = levy_b_total = levy_d_total = 0.0

        seq = 0
        for line in self.invoice_line_ids.filtered(lambda l: l.display_type == 'product'):
            seq += 1
            item = self._prepare_evat_item(line, seq)
            items.append(item)

            tax_code = item['TAX_CODE']
            totals[tax_code] += line.price_subtotal
            tax_totals[tax_code] += item['TAX_AMT']
            levy_a_total += item['LEVY_A_AMT']
            levy_b_total += item['LEVY_B_AMT']
            levy_d_total += item['LEVY_D_AMT']

        trans_type = 'REFUND' if self.move_type == 'out_refund' else 'SALE'

        payload = {
            'TRANS_TYPE': trans_type,
            'INVOICE_NUMBER': self.name or '',
            'INVOICE_DATE': self._get_evat_date(),
            'INVOICE_TIME': self._get_evat_datetime(),
            'CLIENT_TIN': self.partner_id.vat or '',
            'CLIENT_NAME': (self.partner_id.name or 'CASH CUSTOMER')[:100],
            'CLIENT_ADDRESS': (self.partner_id.contact_address or '')[:200],
            'ITEMS': items,
            'TAX_A_BASE': round(totals['TAX_A'], 2),
            'TAX_A_AMT': round(tax_totals['TAX_A'], 2),
            'TAX_B_BASE': round(totals['TAX_B'], 2),
            'TAX_B_AMT': round(tax_totals['TAX_B'], 2),
            'TAX_C_BASE': round(totals['TAX_C'], 2),
            'TAX_C_AMT': round(tax_totals['TAX_C'], 2),
            'TAX_D_BASE': round(totals['TAX_D'], 2),
            'TAX_D_AMT': round(tax_totals['TAX_D'], 2),
            'TAX_E_BASE': round(totals['TAX_E'], 2),
            'TAX_E_AMT': round(tax_totals['TAX_E'], 2),
            'LEVY_A_AMT': round(levy_a_total, 2),
            'LEVY_B_AMT': round(levy_b_total, 2),
            'LEVY_D_AMT': round(levy_d_total, 2),
            'TOTAL_BASE': round(sum(totals.values()), 2),
            'TOTAL_TAX': round(sum(tax_totals.values()), 2),
            'TOTAL_LEVY': round(levy_a_total + levy_b_total + levy_d_total, 2),
            'TOTAL_AMOUNT': round(self.amount_total, 2),
        }

        return payload

    def action_submit_evat(self):
        """Submit invoice to GRA E-VAT."""
        self.ensure_one()

        if self.evat_submitted:
            raise UserError(_('This invoice has already been submitted to E-VAT.'))

        if self.state != 'posted':
            raise UserError(_('Only posted invoices can be submitted to E-VAT.'))

        config = self.env['ghana.evat.config'].get_config(self.company_id)
        payload = self._prepare_evat_payload()

        _logger.info('Submitting invoice %s to GRA E-VAT', self.name)

        try:
            result = config._call_api('post_receipt_Json.jsp', payload)

            self.write({
                'evat_submitted': True,
                'evat_submit_date': fields.Datetime.now(),
                'evat_sdc_id': result.get('SDC_ID', result.get('sdc_id', '')),
                'evat_sdc_time': result.get('SDC_TIME', result.get('sdc_time', '')),
                'evat_invoice_number': result.get('INVOICE_NUMBER', result.get('invoice_number', '')),
                'evat_internal_data': result.get('INTERNAL_DATA', result.get('internalData', '')),
                'evat_signature': result.get('SIGNATURE', result.get('signature', '')),
                'evat_qrcode_url': result.get('QRCODE_URL', result.get('QRCodeURL', '')),
                'evat_response': json.dumps(result, indent=2),
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Invoice submitted to E-VAT. SDC: %s') % self.evat_sdc_id,
                    'type': 'success',
                }
            }
        except UserError:
            raise
        except Exception as e:
            _logger.exception('E-VAT submission failed for %s', self.name)
            raise UserError(_('E-VAT submission failed: %s') % str(e))
