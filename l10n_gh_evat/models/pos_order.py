# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

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
    evat_qrcode = fields.Char(string='QR Code URL', copy=False, readonly=True,
                              help='URL for verification QR code')
    evat_submit_date = fields.Datetime(string='E-VAT Submit Date', copy=False, readonly=True)
    evat_response = fields.Text(string='E-VAT Response', copy=False, readonly=True)

    def _get_evat_date(self, dt=None):
        """Format date for GRA E-VAT v8.2: YYYY-MM-DD"""
        dt = dt or self.date_order or fields.Datetime.now()
        if isinstance(dt, str):
            dt = fields.Datetime.from_string(dt)
        return dt.strftime('%Y-%m-%d')

    def _get_evat_item_category(self, line):
        """
        Determine GRA item category code for POS line.
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
        """Prepare a single POS order line for GRA E-VAT v8.2."""
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

        discount_amt = round(line.discount * line.price_unit * line.qty / 100, 2) if line.discount else 0

        return {
            'itemCode': line.product_id.default_code or f'PROD{line.product_id.id}' if line.product_id else 'ITEM',
            'itemCategory': item_category,
            'expireDate': '',
            'description': (line.full_product_name or line.product_id.name or 'Item')[:100],
            'quantity': str(round(line.qty, 3)),
            'levyAmountA': levy_a,
            'levyAmountB': levy_b,
            'levyAmountD': levy_d,
            'levyAmountE': levy_e,
            'discountAmount': discount_amt,
            'exciseAmount': 0,
            'batchCode': '',
            'unitPrice': str(round(line.price_unit, 2)),
        }

    def _prepare_evat_payload(self):
        """Prepare the full GRA E-VAT v8.2 payload for POS order."""
        self.ensure_one()

        config = self.env['ghana.evat.config'].get_config(self.company_id)

        items = []
        total_levy = 0.0
        total_vat = 0.0
        total_discount = 0.0

        for line in self.lines:
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

        # Determine flag
        total_amount = self.amount_total
        flag = 'REFUND' if total_amount < 0 else 'INVOICE'

        # Customer info
        partner = self.partner_id
        client_name = partner.name if partner else 'Cash Customer'
        client_tin = partner.vat if partner and partner.vat else 'C0000000000'

        payload = {
            'currency': self.currency_id.name or 'GHS',
            'exchangeRate': '1.0',
            'invoiceNumber': self.pos_reference or self.name or '',
            'totalLevy': round(total_levy, 2),
            'userName': config.user_name,
            'flag': flag,
            'calculationType': 'EXCLUSIVE',
            'totalVat': round(total_vat, 2),
            'transactionDate': self._get_evat_date(),
            'totalAmount': round(abs(total_amount), 2),
            'totalExciseAmount': 0.00,
            'businessPartnerName': client_name[:100],
            'businessPartnerTin': client_tin,
            'saleType': 'NORMAL',
            'discountType': 'GENERAL',
            'taxType': 'STANDARD',
            'discountAmount': round(total_discount, 2),
            'reference': '',
            'groupReferenceId': '',
            'purchaseOrderReference': '',
            'items': items,
        }

        return payload

    def action_submit_evat(self):
        """Submit POS order to GRA E-VAT v8.2."""
        self.ensure_one()

        if self.evat_submitted:
            raise UserError(_('This receipt has already been submitted to E-VAT.'))

        if self.state not in ('paid', 'done', 'invoiced'):
            raise UserError(_('Only paid orders can be submitted to E-VAT.'))

        config = self.env['ghana.evat.config'].get_config(self.company_id)
        payload = self._prepare_evat_payload()

        _logger.info('Submitting POS order %s to GRA E-VAT v8.2', self.name)

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
                'evat_qrcode': response_data.get('qr_code', ''),
                'evat_response': json.dumps(result, indent=2),
            })

            return {
                'evat_submitted': True,
                'evat_sdc_id': self.evat_sdc_id,
                'evat_receipt_number': self.evat_receipt_number,
                'evat_sdc_time': self.evat_sdc_time,
                'evat_qrcode': self.evat_qrcode,
            }

        except UserError:
            raise
        except Exception as e:
            _logger.exception('E-VAT submission failed for POS order %s', self.name)
            raise UserError(_('E-VAT submission failed: %s') % str(e))

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
            'evat_qrcode': self.evat_qrcode or '',
        }
