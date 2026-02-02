# Part of VumaERP. See LICENSE file for full copyright and licensing details.

import json
import logging
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # E-VAT Submission Fields
    evat_submitted = fields.Boolean(
        string='Submitted to E-VAT',
        default=False,
        copy=False,
        readonly=True,
        help='Indicates if invoice has been submitted to GRA E-VAT',
    )
    evat_sdc_id = fields.Char(
        string='SDC ID',
        copy=False,
        readonly=True,
        help='Sales Data Controller ID from GRA',
    )
    evat_sdc_time = fields.Char(
        string='SDC Time',
        copy=False,
        readonly=True,
        help='SDC timestamp from GRA',
    )
    evat_invoice_number = fields.Char(
        string='E-VAT Invoice Number',
        copy=False,
        readonly=True,
        help='Invoice number assigned by GRA E-VAT',
    )
    evat_internal_data = fields.Char(
        string='Internal Data',
        copy=False,
        readonly=True,
        help='Internal data hash from GRA',
    )
    evat_signature = fields.Char(
        string='Receipt Signature',
        copy=False,
        readonly=True,
        help='Digital signature from GRA',
    )
    evat_qrcode_url = fields.Char(
        string='QR Code URL',
        copy=False,
        readonly=True,
        help='URL for QR code verification',
    )
    evat_submit_date = fields.Datetime(
        string='Submission Date',
        copy=False,
        readonly=True,
        help='Date/time of E-VAT submission',
    )
    evat_response = fields.Text(
        string='E-VAT Response',
        copy=False,
        readonly=True,
        help='Full JSON response from GRA E-VAT',
    )

    def _get_evat_date(self, dt=None):
        """
        Format date for GRA E-VAT API.

        Args:
            dt: datetime object or None for invoice date

        Returns:
            str: Date formatted as YYYY-MM-DD
        """
        if dt is None:
            dt = self.invoice_date or fields.Date.today()
        if isinstance(dt, datetime):
            return dt.strftime('%Y-%m-%d')
        return str(dt)

    def _get_evat_datetime(self, dt=None):
        """
        Format datetime for GRA E-VAT API.

        Args:
            dt: datetime object or None for now

        Returns:
            str: Datetime formatted as YYYY-MM-DD HH:MM:SS
        """
        if dt is None:
            dt = datetime.now()
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def _get_evat_tax_code(self, line):
        """
        Get GRA tax code for an invoice line.

        Args:
            line: account.move.line record

        Returns:
            str: GRA tax code (TAX_A through TAX_E)
        """
        TaxCode = self.env['ghana.evat.tax.code']

        # Get the first tax on the line
        tax = line.tax_ids[:1] if line.tax_ids else None
        return TaxCode.map_odoo_tax_to_gra(tax)

    def _get_evat_levy_amounts(self, line, tax_code):
        """
        Calculate levy amounts for an invoice line.

        Under VAT Act 1151 (January 2026):
        - NHIL (LEVY_A): 2.5%
        - GETFund (LEVY_B): 2.5%
        - COVID Levy: Abolished

        Args:
            line: account.move.line record
            tax_code: GRA tax code

        Returns:
            dict: Levy amounts
        """
        TaxCode = self.env['ghana.evat.tax.code']
        levies = {
            'LEVY_A': 0.0,  # NHIL
            'LEVY_B': 0.0,  # GETFund
            'LEVY_D': 0.0,  # Tourism/CST
        }

        if tax_code != 'TAX_B':
            return levies

        base_amount = line.price_subtotal

        # NHIL: 2.5%
        nhil_rate = TaxCode.get_tax_rate('LEVY_A')
        levies['LEVY_A'] = round(base_amount * nhil_rate, 2)

        # GETFund: 2.5%
        getfund_rate = TaxCode.get_tax_rate('LEVY_B')
        levies['LEVY_B'] = round(base_amount * getfund_rate, 2)

        return levies

    def _prepare_evat_item(self, line, sequence):
        """
        Prepare invoice line data for GRA E-VAT API.

        Args:
            line: account.move.line record
            sequence: Item sequence number

        Returns:
            dict: Line item data for API payload
        """
        tax_code = self._get_evat_tax_code(line)
        levies = self._get_evat_levy_amounts(line, tax_code)

        # Calculate tax amount
        TaxCode = self.env['ghana.evat.tax.code']
        tax_rate = TaxCode.get_tax_rate(tax_code)
        tax_amount = round(line.price_subtotal * tax_rate, 2)

        return {
            'ITEM_SEQ': sequence,
            'ITEM_CODE': line.product_id.default_code or str(line.product_id.id) or 'ITEM',
            'ITEM_DESC': (line.name or line.product_id.name or 'Item')[:100],
            'UNIT_PRICE': round(line.price_unit, 2),
            'QUANTITY': round(line.quantity, 3),
            'DISCOUNT_AMT': round((line.price_unit * line.quantity) - line.price_subtotal, 2),
            'TAX_CODE': tax_code,
            'TAX_RATE': round(tax_rate * 100, 2),
            'TAX_AMT': tax_amount,
            'LEVY_A_AMT': levies['LEVY_A'],
            'LEVY_B_AMT': levies['LEVY_B'],
            'LEVY_D_AMT': levies['LEVY_D'],
            'TOTAL_AMT': round(line.price_subtotal + tax_amount + sum(levies.values()), 2),
        }

    def _prepare_evat_payload(self):
        """
        Prepare complete payload for GRA E-VAT submission.

        Based on GRA E-VAT API documentation, the payload includes:
        - Header information (invoice number, date, customer details)
        - Line items with tax calculations
        - Totals by tax code

        Returns:
            dict: Complete API payload
        """
        self.ensure_one()

        if self.move_type not in ('out_invoice', 'out_refund'):
            raise UserError(_('Only customer invoices can be submitted to E-VAT.'))

        if self.state != 'posted':
            raise UserError(_('Only posted invoices can be submitted to E-VAT.'))

        if self.evat_submitted:
            raise UserError(_('This invoice has already been submitted to E-VAT.'))

        # Determine transaction type
        trans_type = 'SALE' if self.move_type == 'out_invoice' else 'REFUND'

        # Customer information
        customer = self.partner_id
        customer_tin = customer.vat or ''

        # Prepare line items
        items = []
        totals_by_tax = {}

        for seq, line in enumerate(self.invoice_line_ids.filtered(lambda l: l.display_type == 'product'), start=1):
            item = self._prepare_evat_item(line, seq)
            items.append(item)

            # Accumulate totals by tax code
            tax_code = item['TAX_CODE']
            if tax_code not in totals_by_tax:
                totals_by_tax[tax_code] = {
                    'base': 0.0,
                    'tax': 0.0,
                    'levy_a': 0.0,
                    'levy_b': 0.0,
                    'levy_d': 0.0,
                }
            totals_by_tax[tax_code]['base'] += line.price_subtotal
            totals_by_tax[tax_code]['tax'] += item['TAX_AMT']
            totals_by_tax[tax_code]['levy_a'] += item['LEVY_A_AMT']
            totals_by_tax[tax_code]['levy_b'] += item['LEVY_B_AMT']
            totals_by_tax[tax_code]['levy_d'] += item['LEVY_D_AMT']

        # Calculate totals
        total_base = sum(t['base'] for t in totals_by_tax.values())
        total_tax = sum(t['tax'] for t in totals_by_tax.values())
        total_levy_a = sum(t['levy_a'] for t in totals_by_tax.values())
        total_levy_b = sum(t['levy_b'] for t in totals_by_tax.values())
        total_levy_d = sum(t['levy_d'] for t in totals_by_tax.values())
        total_amount = total_base + total_tax + total_levy_a + total_levy_b + total_levy_d

        # Build payload
        payload = {
            # Transaction header
            'TRANS_TYPE': trans_type,
            'INVOICE_NUMBER': self.name,
            'INVOICE_DATE': self._get_evat_date(),
            'INVOICE_TIME': self._get_evat_datetime(),

            # Customer details
            'CLIENT_TIN': customer_tin,
            'CLIENT_NAME': (customer.name or 'CASH CUSTOMER')[:100],
            'CLIENT_ADDRESS': (customer.contact_address or '')[:200],

            # Items
            'ITEMS': items,

            # Tax totals by code
            'TAX_A_BASE': round(totals_by_tax.get('TAX_A', {}).get('base', 0), 2),
            'TAX_A_AMT': round(totals_by_tax.get('TAX_A', {}).get('tax', 0), 2),
            'TAX_B_BASE': round(totals_by_tax.get('TAX_B', {}).get('base', 0), 2),
            'TAX_B_AMT': round(totals_by_tax.get('TAX_B', {}).get('tax', 0), 2),
            'TAX_C_BASE': round(totals_by_tax.get('TAX_C', {}).get('base', 0), 2),
            'TAX_C_AMT': round(totals_by_tax.get('TAX_C', {}).get('tax', 0), 2),
            'TAX_D_BASE': round(totals_by_tax.get('TAX_D', {}).get('base', 0), 2),
            'TAX_D_AMT': round(totals_by_tax.get('TAX_D', {}).get('tax', 0), 2),
            'TAX_E_BASE': round(totals_by_tax.get('TAX_E', {}).get('base', 0), 2),
            'TAX_E_AMT': round(totals_by_tax.get('TAX_E', {}).get('tax', 0), 2),

            # Levy totals
            'LEVY_A_AMT': round(total_levy_a, 2),  # NHIL
            'LEVY_B_AMT': round(total_levy_b, 2),  # GETFund
            'LEVY_D_AMT': round(total_levy_d, 2),  # Tourism/CST

            # Grand totals
            'TOTAL_BASE': round(total_base, 2),
            'TOTAL_TAX': round(total_tax, 2),
            'TOTAL_LEVY': round(total_levy_a + total_levy_b + total_levy_d, 2),
            'TOTAL_AMOUNT': round(total_amount, 2),
        }

        return payload

    def action_submit_evat(self):
        """
        Submit invoice to GRA E-VAT system.

        This action:
        1. Validates the invoice is ready for submission
        2. Prepares the API payload
        3. Calls the GRA E-VAT API
        4. Stores the response (SDC code, signature, QR code URL)

        Returns:
            dict: Notification action with result
        """
        self.ensure_one()

        # Get E-VAT configuration
        config = self.env['ghana.evat.config'].get_config(self.company_id)

        # Prepare payload
        payload = self._prepare_evat_payload()

        _logger.info(
            "Submitting invoice %s to GRA E-VAT (%s)",
            self.name, config.environment
        )

        try:
            # Call GRA E-VAT API
            response = config._call_api('post_receipt_Json.jsp', payload)

            # Process response
            # GRA returns SDC information on successful submission
            self.write({
                'evat_submitted': True,
                'evat_submit_date': fields.Datetime.now(),
                'evat_sdc_id': response.get('SDC_ID', response.get('sdc_id', '')),
                'evat_sdc_time': response.get('SDC_TIME', response.get('sdc_time', '')),
                'evat_invoice_number': response.get('INVOICE_NUMBER', response.get('invoice_number', '')),
                'evat_internal_data': response.get('INTERNAL_DATA', response.get('internalData', '')),
                'evat_signature': response.get('SIGNATURE', response.get('signature', '')),
                'evat_qrcode_url': response.get('QRCODE_URL', response.get('QRCodeURL', '')),
                'evat_response': json.dumps(response, indent=2),
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('E-VAT Submission Successful'),
                    'message': _('Invoice %s submitted to GRA. SDC ID: %s') % (
                        self.name,
                        self.evat_sdc_id or 'N/A'
                    ),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except UserError:
            raise
        except Exception as e:
            _logger.exception("E-VAT submission failed for invoice %s", self.name)
            raise UserError(_('E-VAT submission failed: %s') % str(e))

    def action_view_evat_response(self):
        """
        View the full E-VAT response in a popup.

        Returns:
            dict: Action to display response
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('E-VAT Response'),
            'res_model': 'account.move',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'show_evat_response': True},
        }
