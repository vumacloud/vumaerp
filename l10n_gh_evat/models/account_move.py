# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # E-VAT Fields (v8.2)
    evat_submitted = fields.Boolean(string='Submitted to E-VAT', copy=False)
    evat_sdc_id = fields.Char(string='SDC ID', copy=False, readonly=True,
                              help='ysdcid - Sales Data Controller ID')
    evat_sdc_time = fields.Char(string='SDC Time', copy=False, readonly=True,
                                help='ysdctime - Timestamp from SDC')
    evat_receipt_number = fields.Char(string='Receipt Number', copy=False, readonly=True,
                                      help='ysdcrecnum - SDC Receipt Number')
    evat_internal_data = fields.Char(string='Internal Data', copy=False, readonly=True,
                                     help='ysdcintdata - Internal reference data')
    evat_signature = fields.Char(string='Signature', copy=False, readonly=True,
                                 help='ysdcregsig - Digital signature')
    evat_invoice_number = fields.Char(string='E-VAT Invoice No', copy=False, readonly=True)
    evat_qrcode = fields.Char(string='QR Code URL', copy=False, readonly=True,
                              help='URL for verification QR code')
    evat_submit_date = fields.Datetime(string='E-VAT Submit Date', copy=False, readonly=True)
    evat_response = fields.Text(string='E-VAT Response', copy=False, readonly=True)

    def _get_evat_date(self, dt=None):
        """Format date for GRA E-VAT v8.2: YYYY-MM-DD"""
        dt = dt or self.invoice_date or fields.Date.today()
        if isinstance(dt, str):
            dt = fields.Date.from_string(dt)
        return dt.strftime('%Y-%m-%d')

    def _get_evat_calculation_type(self):
        """Determine if prices are tax inclusive or exclusive."""
        # Check if any line has tax included in price
        for line in self.invoice_line_ids.filtered(lambda l: l.display_type == 'product'):
            if line.tax_ids and any(t.price_include for t in line.tax_ids):
                return 'INCLUSIVE'
        return 'EXCLUSIVE'

    def _get_evat_tax_type(self, line):
        """Determine tax type for a line."""
        if not line.tax_ids:
            return 'EXEMPT'

        tax = line.tax_ids[0]
        if tax.amount == 0:
            return 'EXEMPT'
        elif tax.amount == 3:
            return 'FLAT'
        else:
            return 'STANDARD'

    def _get_evat_item_category(self, line):
        """
        Determine GRA item category code.
        Valid values: "", "CST", "TRSM", "EXM", "RNT", "EXC_PLASTIC"
        """
        if not line.tax_ids:
            return 'EXM'  # Zero rated/Exempt

        tax = line.tax_ids[0]
        tax_name = (tax.name or '').upper()

        # Check tax name for category hints
        if 'CST' in tax_name or 'COMMUNICATION' in tax_name:
            return 'CST'
        elif 'TOURISM' in tax_name or 'TRSM' in tax_name:
            return 'TRSM'
        elif 'EXEMPT' in tax_name or tax.amount == 0:
            return 'EXM'
        elif 'RENT' in tax_name:
            return 'RNT'
        elif 'PLASTIC' in tax_name or 'EXCISE' in tax_name:
            return 'EXC_PLASTIC'

        return ''  # Standard taxable item

    def _prepare_evat_item(self, line):
        """Prepare a single invoice line for GRA E-VAT v8.2."""
        # Calculate levy amounts based on item category
        base_amt = line.price_subtotal
        levy_a = levy_b = levy_d = levy_e = 0.0

        item_category = self._get_evat_item_category(line)

        # Calculate levies based on category
        # LEVY_A: NHIL 2.5%, LEVY_B: GETFund 2.5%, LEVY_D: CST 5%, LEVY_E: Tourism 1%
        if item_category == '':  # Standard taxable
            levy_a = round(base_amt * 0.025, 2)  # NHIL 2.5%
            levy_b = round(base_amt * 0.025, 2)  # GETFund 2.5%
        elif item_category == 'CST':
            levy_d = round(base_amt * 0.05, 2)  # CST 5%
        elif item_category == 'TRSM':
            levy_e = round(base_amt * 0.01, 2)  # Tourism 1%
        # EXM, RNT, EXC_PLASTIC have zero levies

        return {
            'itemCode': line.product_id.default_code or f'PROD{line.product_id.id}' if line.product_id else 'ITEM',
            'itemCategory': item_category,
            'expireDate': '',
            'description': (line.name or line.product_id.name or 'Item')[:100],
            'quantity': str(round(line.quantity, 3)),
            'levyAmountA': levy_a,
            'levyAmountB': levy_b,
            'levyAmountD': levy_d,
            'levyAmountE': levy_e,
            'discountAmount': round((line.price_unit * line.quantity) - base_amt, 2) if line.discount else 0,
            'exciseAmount': 0,
            'batchCode': '',
            'unitPrice': str(round(line.price_unit, 2)),
        }

    def _prepare_evat_payload(self):
        """Prepare the full GRA E-VAT v8.2 payload."""
        self.ensure_one()

        if self.move_type not in ('out_invoice', 'out_refund'):
            raise UserError(_('Only customer invoices can be submitted to E-VAT.'))

        config = self.env['ghana.evat.config'].get_config(self.company_id)

        items = []
        total_levy = 0.0
        total_vat = 0.0
        total_discount = 0.0

        for line in self.invoice_line_ids.filtered(lambda l: l.display_type == 'product'):
            item = self._prepare_evat_item(line)
            items.append(item)

            # Accumulate totals
            total_levy += item['levyAmountA'] + item['levyAmountB'] + item['levyAmountD'] + item['levyAmountE']
            total_discount += item['discountAmount']

            # Calculate VAT for this line
            if line.tax_ids:
                for tax in line.tax_ids:
                    if tax.amount > 0 and 'VAT' in tax.name.upper():
                        total_vat += round(line.price_subtotal * tax.amount / 100, 2)

        # Determine flag (INVOICE or REFUND)
        flag = 'REFUND' if self.move_type == 'out_refund' else 'INVOICE'

        # Get calculation type
        calc_type = self._get_evat_calculation_type()

        payload = {
            'currency': self.currency_id.name or 'GHS',
            'exchangeRate': str(self.currency_id.rate or 1.0),
            'invoiceNumber': self.name or '',
            'totalLevy': round(total_levy, 2),
            'userName': config.user_name,
            'flag': flag,
            'calculationType': calc_type,
            'totalVat': round(total_vat, 2),
            'transactionDate': self._get_evat_date(),
            'totalAmount': round(self.amount_total, 2),
            'totalExciseAmount': 0.00,
            'businessPartnerName': (self.partner_id.name or 'Cash Customer')[:100],
            'businessPartnerTin': self.partner_id.vat or 'C0000000000',
            'saleType': 'NORMAL',
            'discountType': 'GENERAL' if total_discount > 0 else 'GENERAL',
            'taxType': 'STANDARD',
            'discountAmount': round(total_discount, 2),
            'reference': self.ref or '',
            'groupReferenceId': '',
            'purchaseOrderReference': self.invoice_origin or '',
            'items': items,
        }

        return payload

    def action_submit_evat(self):
        """Submit invoice to GRA E-VAT v8.2."""
        self.ensure_one()

        if self.evat_submitted:
            raise UserError(_('This invoice has already been submitted to E-VAT.'))

        if self.state != 'posted':
            raise UserError(_('Only posted invoices can be submitted to E-VAT.'))

        config = self.env['ghana.evat.config'].get_config(self.company_id)
        payload = self._prepare_evat_payload()

        _logger.info('Submitting invoice %s to GRA E-VAT v8.2', self.name)

        try:
            result = config._call_api('invoice', payload)

            # Parse v8.2 response structure:
            # {"response": {"message": {...}, "qr_code": "...", "status": "SUCCESS"}}
            response_data = result.get('response', result)
            message = response_data.get('message', {})

            self.write({
                'evat_submitted': True,
                'evat_submit_date': fields.Datetime.now(),
                'evat_sdc_id': message.get('ysdcid', ''),
                'evat_receipt_number': message.get('ysdcrecnum', ''),
                'evat_sdc_time': message.get('ysdctime', ''),
                'evat_internal_data': message.get('ysdcintdata', ''),
                'evat_signature': message.get('ysdcregsig', ''),
                'evat_invoice_number': message.get('num', self.name),
                'evat_qrcode': response_data.get('qr_code', ''),
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
