# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    # E-VAT Fields
    evat_submitted = fields.Boolean(string='Submitted to E-VAT', copy=False)
    evat_sdc_id = fields.Char(string='SDC ID', copy=False, readonly=True)
    evat_sdc_time = fields.Char(string='SDC Time', copy=False, readonly=True)
    evat_receipt_number = fields.Char(string='E-VAT Receipt No', copy=False, readonly=True)
    evat_internal_data = fields.Char(string='Internal Data', copy=False, readonly=True)
    evat_signature = fields.Char(string='Signature', copy=False, readonly=True)
    evat_qrcode_url = fields.Char(string='QR Code URL', copy=False, readonly=True)
    evat_submit_date = fields.Datetime(string='E-VAT Submit Date', copy=False, readonly=True)
    evat_response = fields.Text(string='E-VAT Response', copy=False, readonly=True)

    def _get_evat_date(self, dt=None):
        """Format date for GRA E-VAT: YYYY-MM-DD"""
        dt = dt or self.date_order or fields.Datetime.now()
        if isinstance(dt, str):
            dt = fields.Datetime.from_string(dt)
        return dt.strftime('%Y-%m-%d')

    def _get_evat_datetime(self, dt=None):
        """Format datetime for GRA E-VAT: YYYY-MM-DD HH:MM:SS"""
        dt = dt or self.date_order or datetime.now()
        if isinstance(dt, str):
            dt = fields.Datetime.from_string(dt)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def _get_evat_tax_code(self, tax):
        """Map Odoo tax to GRA tax code."""
        TaxCode = self.env['ghana.evat.tax.code']
        return TaxCode.map_odoo_tax_to_gra(tax)

    def _prepare_evat_item(self, line, seq):
        """Prepare a single POS order line for GRA E-VAT."""
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
            'ITEM_DESC': (line.full_product_name or line.product_id.name or 'Item')[:100],
            'UNIT_PRICE': round(line.price_unit, 2),
            'QUANTITY': round(line.qty, 3),
            'DISCOUNT_AMT': round(line.discount * line.price_unit * line.qty / 100, 2) if line.discount else 0.0,
            'TAX_CODE': tax_code,
            'TAX_RATE': round(tax_rate * 100, 2),
            'TAX_AMT': tax_amt,
            'LEVY_A_AMT': levy_a,
            'LEVY_B_AMT': levy_b,
            'LEVY_D_AMT': levy_d,
            'TOTAL_AMT': round(base_amt + tax_amt + levy_a + levy_b + levy_d, 2),
        }

    def _prepare_evat_payload(self):
        """Prepare the full GRA E-VAT payload for POS order."""
        self.ensure_one()

        items = []
        totals = {'TAX_A': 0, 'TAX_B': 0, 'TAX_C': 0, 'TAX_D': 0, 'TAX_E': 0}
        tax_totals = {'TAX_A': 0, 'TAX_B': 0, 'TAX_C': 0, 'TAX_D': 0, 'TAX_E': 0}
        levy_a_total = levy_b_total = levy_d_total = 0.0

        seq = 0
        for line in self.lines:
            seq += 1
            item = self._prepare_evat_item(line, seq)
            items.append(item)

            tax_code = item['TAX_CODE']
            totals[tax_code] += line.price_subtotal
            tax_totals[tax_code] += item['TAX_AMT']
            levy_a_total += item['LEVY_A_AMT']
            levy_b_total += item['LEVY_B_AMT']
            levy_d_total += item['LEVY_D_AMT']

        # Determine transaction type
        total_amount = self.amount_total
        trans_type = 'REFUND' if total_amount < 0 else 'SALE'

        # Customer info
        partner = self.partner_id
        client_name = partner.name if partner else 'CASH CUSTOMER'
        client_tin = partner.vat if partner else ''
        client_address = partner.contact_address if partner else ''

        payload = {
            'TRANS_TYPE': trans_type,
            'RECEIPT_NUMBER': self.pos_reference or self.name or '',
            'INVOICE_DATE': self._get_evat_date(),
            'INVOICE_TIME': self._get_evat_datetime(),
            'CLIENT_TIN': client_tin or '',
            'CLIENT_NAME': client_name[:100],
            'CLIENT_ADDRESS': (client_address or '')[:200],
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
            'TOTAL_AMOUNT': round(abs(total_amount), 2),
            'PAYMENT_MODE': self._get_payment_mode(),
        }

        return payload

    def _get_payment_mode(self):
        """Determine payment mode for E-VAT."""
        if not self.payment_ids:
            return 'CASH'

        payment = self.payment_ids[0]
        method_name = payment.payment_method_id.name.upper() if payment.payment_method_id else ''

        if 'CASH' in method_name:
            return 'CASH'
        elif 'CARD' in method_name or 'CREDIT' in method_name or 'DEBIT' in method_name:
            return 'CARD'
        elif 'MOBILE' in method_name or 'MOMO' in method_name:
            return 'MOBILE_MONEY'
        elif 'CHEQUE' in method_name or 'CHECK' in method_name:
            return 'CHEQUE'
        else:
            return 'OTHER'

    def action_submit_evat(self):
        """Submit POS order to GRA E-VAT."""
        self.ensure_one()

        if self.evat_submitted:
            raise UserError(_('This receipt has already been submitted to E-VAT.'))

        if self.state not in ('paid', 'done', 'invoiced'):
            raise UserError(_('Only paid orders can be submitted to E-VAT.'))

        config = self.env['ghana.evat.config'].get_config(self.company_id)
        payload = self._prepare_evat_payload()

        _logger.info('Submitting POS order %s to GRA E-VAT', self.name)

        try:
            result = config._call_api('post_receipt_Json.jsp', payload)

            self.write({
                'evat_submitted': True,
                'evat_submit_date': fields.Datetime.now(),
                'evat_sdc_id': result.get('SDC_ID', result.get('sdc_id', '')),
                'evat_sdc_time': result.get('SDC_TIME', result.get('sdc_time', '')),
                'evat_receipt_number': result.get('RECEIPT_NUMBER', result.get('receipt_number', '')),
                'evat_internal_data': result.get('INTERNAL_DATA', result.get('internalData', '')),
                'evat_signature': result.get('SIGNATURE', result.get('signature', '')),
                'evat_qrcode_url': result.get('QRCODE_URL', result.get('QRCodeURL', '')),
                'evat_response': json.dumps(result, indent=2),
            })

            return {
                'evat_submitted': True,
                'evat_sdc_id': self.evat_sdc_id,
                'evat_receipt_number': self.evat_receipt_number,
                'evat_qrcode_url': self.evat_qrcode_url,
            }

        except UserError:
            raise
        except Exception as e:
            _logger.exception('E-VAT submission failed for POS order %s', self.name)
            raise UserError(_('E-VAT submission failed: %s') % str(e))

    def _submit_evat_auto(self):
        """Auto-submit to E-VAT after payment (called from POS)."""
        for order in self:
            if order.evat_submitted:
                continue
            try:
                order.action_submit_evat()
            except Exception as e:
                _logger.error('Auto E-VAT submission failed for %s: %s', order.name, str(e))

    @api.model
    def _order_fields(self, ui_order):
        """Extend to include E-VAT fields from POS."""
        result = super()._order_fields(ui_order)
        # E-VAT data will be populated after submission
        return result

    @api.model
    def create_from_ui(self, orders, draft=False):
        """Override to auto-submit to E-VAT after order creation."""
        order_ids = super().create_from_ui(orders, draft=draft)

        # Get the created orders
        orders = self.browse([o['id'] for o in order_ids])

        # Auto-submit to E-VAT for paid orders
        for order in orders.filtered(lambda o: o.state in ('paid', 'done') and not o.evat_submitted):
            try:
                # Check if E-VAT is configured
                config = self.env['ghana.evat.config'].search([
                    ('company_id', '=', order.company_id.id)
                ], limit=1)

                if config:
                    order.action_submit_evat()
                    _logger.info('E-VAT auto-submitted for POS order %s', order.name)
            except Exception as e:
                _logger.warning('E-VAT auto-submission failed for %s: %s', order.name, str(e))
                # Don't fail the order creation, just log the warning

        return order_ids

    def get_evat_receipt_data(self):
        """Get E-VAT data for receipt printing."""
        self.ensure_one()
        return {
            'evat_submitted': self.evat_submitted,
            'evat_sdc_id': self.evat_sdc_id or '',
            'evat_sdc_time': self.evat_sdc_time or '',
            'evat_receipt_number': self.evat_receipt_number or '',
            'evat_qrcode_url': self.evat_qrcode_url or '',
        }
