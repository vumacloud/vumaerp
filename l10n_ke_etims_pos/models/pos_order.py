# -*- coding: utf-8 -*-
"""
POS Order eTIMS Integration

Handles submission of Point of Sale orders to KRA eTIMS.
POS transactions are submitted when:
1. Payment is completed at the POS (immediate submission)
2. Session is closed (batch submission for any missed orders)

This is critical for SME compliance as POS is a primary sales channel.

Key Features:
- Real-time submission when payment is finalized
- Offline queue for submission when connectivity is lost
- Batch submission at session close
- POS refund/return handling
"""
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    # eTIMS Submission Fields
    etims_submitted = fields.Boolean(
        string='Submitted to eTIMS',
        copy=False,
        help='Indicates if this POS order has been submitted to KRA eTIMS'
    )
    etims_invoice_number = fields.Integer(
        string='eTIMS Invoice Number',
        copy=False,
        readonly=True,
        help='Sequential numeric invoice number for eTIMS (invcNo)'
    )
    etims_sdc_id = fields.Char(
        string='SDC ID',
        copy=False,
        readonly=True,
        help='SDC/CU ID from device initialization'
    )
    etims_rcpt_no = fields.Char(
        string='Receipt No',
        copy=False,
        readonly=True,
        help='Receipt number from KRA eTIMS'
    )
    etims_cu_invoice_number = fields.Char(
        string='CU Invoice Number',
        copy=False,
        readonly=True,
        compute='_compute_etims_cu_invoice_number',
        store=True,
        help='Formatted CU Invoice Number: {CU_ID}/{Receipt_Number}'
    )
    etims_intrl_data = fields.Char(
        string='Internal Data',
        copy=False,
        readonly=True
    )
    etims_rcpt_sign = fields.Char(
        string='Receipt Signature',
        copy=False,
        readonly=True
    )
    etims_sdc_datetime = fields.Char(
        string='SDC DateTime',
        copy=False,
        readonly=True,
        help='Date/time from OSCU/VSCU'
    )
    etims_submit_date = fields.Datetime(
        string='eTIMS Submit Date',
        copy=False,
        readonly=True
    )
    etims_response = fields.Text(
        string='eTIMS Response',
        copy=False,
        readonly=True
    )
    etims_submission_error = fields.Text(
        string='eTIMS Submission Error',
        copy=False,
        help='Error message if submission failed - for retry'
    )

    # Receipt type per TIS spec Section 4
    etims_transaction_type = fields.Selection([
        ('NORMAL', 'Normal'),
        ('COPY', 'Copy'),
        ('TRAINING', 'Training'),
        ('PROFORMA', 'Proforma'),
    ], string='Transaction Type', default='NORMAL', copy=False,
       help='Transaction type per TIS spec: NORMAL, COPY, TRAINING, or PROFORMA')

    etims_receipt_type_label = fields.Char(
        string='Receipt Type',
        compute='_compute_etims_receipt_type_label',
        store=True,
        help='Receipt type label per TIS spec (NS, NC, CS, CC, TS, TC, PS)'
    )

    @api.depends('etims_transaction_type', 'amount_total')
    def _compute_etims_receipt_type_label(self):
        """Compute receipt type label per TIS spec Section 4."""
        for order in self:
            is_refund = order.amount_total < 0
            receipt_type = 'CREDIT_NOTE' if is_refund else 'SALES'
            trans_type = order.etims_transaction_type or 'NORMAL'

            labels = {
                ('NORMAL', 'SALES'): 'NS',
                ('NORMAL', 'CREDIT_NOTE'): 'NC',
                ('COPY', 'SALES'): 'CS',
                ('COPY', 'CREDIT_NOTE'): 'CC',
                ('TRAINING', 'SALES'): 'TS',
                ('TRAINING', 'CREDIT_NOTE'): 'TC',
                ('PROFORMA', 'SALES'): 'PS',
            }
            order.etims_receipt_type_label = labels.get((trans_type, receipt_type), 'NS')

    def get_formatted_internal_data(self):
        """Get internal data formatted with dashes per TIS spec."""
        self.ensure_one()
        return self._format_with_dashes(self.etims_intrl_data)

    def get_formatted_receipt_signature(self):
        """Get receipt signature formatted with dashes per TIS spec."""
        self.ensure_one()
        return self._format_with_dashes(self.etims_rcpt_sign)

    def _format_with_dashes(self, data, group_size=4):
        """Format data with dashes after every Nth character."""
        if not data:
            return ''
        clean_data = ''.join(c for c in str(data) if c not in '- \t\n')
        groups = [clean_data[i:i + group_size] for i in range(0, len(clean_data), group_size)]
        return '-'.join(groups)

    def get_etims_qr_content(self):
        """Generate QR code content per TIS spec Section 6.23.8."""
        self.ensure_one()
        if not self.etims_submitted:
            return ''

        # Format date as ddmmyyyy
        sdc_datetime = self.etims_sdc_datetime or ''
        if sdc_datetime and len(sdc_datetime) >= 14:
            date_str = sdc_datetime[6:8] + sdc_datetime[4:6] + sdc_datetime[0:4]
            time_str = sdc_datetime[8:14]
        else:
            from datetime import datetime
            now = datetime.now()
            date_str = now.strftime('%d%m%Y')
            time_str = now.strftime('%H%M%S')

        parts = [
            date_str,
            time_str,
            str(self.etims_sdc_id or ''),
            str(self.etims_rcpt_no or ''),
            str(self.etims_intrl_data or ''),
            str(self.etims_rcpt_sign or ''),
        ]
        return '#'.join(parts)

    def get_etims_qr_image(self):
        """Generate QR code image as base64."""
        self.ensure_one()
        content = self.get_etims_qr_content()
        if not content:
            return False

        try:
            import qrcode
            import io
            import base64

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(content)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except ImportError:
            _logger.warning('qrcode library not installed')
            return False
        except Exception as e:
            _logger.error('Failed to generate QR code: %s', str(e))
            return False

    @api.depends('etims_sdc_id', 'etims_rcpt_no')
    def _compute_etims_cu_invoice_number(self):
        """Compute CU Invoice Number in format: {CU_ID}/{Receipt_Number}"""
        for order in self:
            if order.etims_sdc_id and order.etims_rcpt_no:
                order.etims_cu_invoice_number = f"{order.etims_sdc_id}/{order.etims_rcpt_no}"
            else:
                order.etims_cu_invoice_number = False

    def _get_next_etims_invoice_number(self):
        """
        Get the next sequential eTIMS invoice number for POS.
        Per OSCU spec, invcNo must be a NUMBER (integer sequence).
        """
        self.ensure_one()
        # Get the max invoice number for this company from both invoices and POS orders
        self.env.cr.execute("""
            SELECT COALESCE(MAX(max_num), 0) + 1 FROM (
                SELECT MAX(etims_invoice_number) as max_num
                FROM account_move
                WHERE company_id = %s AND etims_invoice_number IS NOT NULL
                UNION ALL
                SELECT MAX(etims_invoice_number) as max_num
                FROM pos_order
                WHERE company_id = %s AND etims_invoice_number IS NOT NULL
            ) combined
        """, (self.company_id.id, self.company_id.id))
        result = self.env.cr.fetchone()
        return result[0] if result else 1

    # Refund-specific fields for POS returns
    # Per OSCU Spec Section 4.16: only codes 01-05 are valid
    etims_refund_reason = fields.Selection([
        ('01', 'Return'),
        ('02', 'Incorrect Information'),
        ('03', 'Omission'),
        ('04', 'Cancellation'),
        ('05', 'Other'),
    ], string='Refund Reason',
       default='01',
       help='Reason code for the refund as required by KRA eTIMS (Section 4.16)')

    etims_original_order_id = fields.Many2one(
        'pos.order',
        string='Original POS Order',
        help='The original POS order being refunded'
    )

    def _is_etims_applicable(self):
        """Check if this POS order should be submitted to eTIMS."""
        self.ensure_one()
        return (
            self.state in ('paid', 'done', 'invoiced') and
            self.company_id.country_id.code == 'KE'
        )

    def _get_etims_date(self, dt=None):
        """Format date for eTIMS: YYYYMMDD"""
        dt = dt or fields.Date.today()
        if isinstance(dt, str):
            dt = fields.Date.from_string(dt)
        return dt.strftime('%Y%m%d')

    def _get_etims_datetime(self, dt=None):
        """Format datetime for eTIMS: YYYYMMDDHHmmss"""
        dt = dt or fields.Datetime.now()
        if isinstance(dt, str):
            dt = fields.Datetime.from_string(dt)
        return dt.strftime('%Y%m%d%H%M%S')

    def _get_etims_tax_code(self, tax):
        """
        Map Odoo tax to eTIMS tax type code.
        A = Exempt, B = 16%, C = 0%, D = Non-VAT, E = 8%
        """
        if not tax:
            return 'D'
        amount = tax.amount if tax else 0
        if amount == 16:
            return 'B'
        elif amount == 8:
            return 'E'
        elif amount == 0:
            return 'C'
        else:
            return 'D'

    def _get_etims_payment_type(self):
        """
        Determine eTIMS payment type based on POS payment methods.

        Per OSCU Spec Section 4.10:
        01=Cash, 02=Credit, 03=Cash/Credit, 04=Bank Check,
        05=Debit/Credit Card, 06=Mobile Money, 07=Other
        """
        self.ensure_one()

        if not self.payment_ids:
            return '01'  # Default cash

        # Check payment methods used
        for payment in self.payment_ids:
            pm = payment.payment_method_id
            pm_name = pm.name.lower() if pm.name else ''

            # Check journal type first
            if pm.journal_id:
                if pm.journal_id.type == 'cash':
                    return '01'  # Cash
                elif pm.journal_id.type == 'bank':
                    # Check for mobile money or cards per spec
                    if any(mm in pm_name for mm in ['mpesa', 'm-pesa', 'mobile', 'airtel', 'safaricom']):
                        return '06'  # Mobile Money (per spec)
                    elif any(card in pm_name for card in ['card', 'visa', 'mastercard', 'debit', 'credit']):
                        return '05'  # Debit/Credit Card (per spec)
                    elif 'check' in pm_name or 'cheque' in pm_name:
                        return '04'  # Bank Check
                    return '02'  # Credit/Bank Transfer

            # Fallback to name-based detection
            if any(cash in pm_name for cash in ['cash', 'ksh', 'kes']):
                return '01'  # Cash
            elif any(mm in pm_name for mm in ['mpesa', 'm-pesa', 'mobile', 'airtel']):
                return '06'  # Mobile Money
            elif any(card in pm_name for card in ['card', 'visa', 'mastercard', 'credit', 'debit']):
                return '05'  # Debit/Credit Card
            elif 'check' in pm_name or 'cheque' in pm_name:
                return '04'  # Bank Check

        return '01'  # Default to cash

    def _prepare_etims_item(self, line, seq):
        """Prepare a single POS order line for eTIMS."""
        product = line.product_id
        product_tmpl = product.product_tmpl_id if product else None

        # Get tax information
        tax = line.tax_ids[:1] if line.tax_ids else line.tax_ids_after_fiscal_position[:1] if hasattr(line, 'tax_ids_after_fiscal_position') else None
        if product_tmpl and product_tmpl.l10n_ke_tax_type:
            tax_code = product_tmpl.l10n_ke_tax_type
        else:
            tax_code = self._get_etims_tax_code(tax)

        tax_amt = tax.amount if tax else 0

        # Get quantities - handle negative for refunds
        qty = abs(line.qty)
        unit_price = line.price_unit
        discount_amt = (abs(unit_price * line.qty) * line.discount / 100) if line.discount else 0
        supply_amt = abs(line.price_subtotal_incl)

        # Calculate tax amounts
        if tax_amt > 0:
            taxable_amt = supply_amt / (1 + tax_amt / 100)
            tax_amount = supply_amt - taxable_amt
        else:
            taxable_amt = supply_amt
            tax_amount = 0

        # Get item codes
        if product:
            item_code = product._get_etims_item_code()[:20]
            item_class_code = product._get_etims_item_class_code()
            unit_codes = product._get_etims_unit_codes()
            pkg_unit_code = unit_codes['pkg_unit']
            qty_unit_code = unit_codes['qty_unit']
        else:
            item_code = 'SVC'
            item_class_code = ''
            pkg_unit_code = 'NT'
            qty_unit_code = 'U'

        return {
            'itemSeq': seq,
            'itemCd': item_code,
            'itemClsCd': item_class_code,
            'itemNm': (line.full_product_name or product.name if product else 'Item')[:200],
            'pkgUnitCd': pkg_unit_code,
            'pkg': 1,
            'qtyUnitCd': qty_unit_code,
            'qty': qty,
            'prc': round(abs(unit_price), 2),
            'splyAmt': round(supply_amt, 2),
            'dcRt': line.discount or 0,
            'dcAmt': round(discount_amt, 2),
            'taxTyCd': tax_code,
            'taxblAmt': round(taxable_amt, 2),
            'taxAmt': round(tax_amount, 2),
            'totAmt': round(supply_amt, 2),
        }

    def _prepare_etims_payload(self):
        """Prepare the full eTIMS sales transaction payload for POS order."""
        self.ensure_one()

        # Prepare items
        items = []
        totals = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
        tax_totals = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}

        seq = 0
        for line in self.lines:
            seq += 1
            item = self._prepare_etims_item(line, seq)
            items.append(item)

            # Accumulate totals by tax type
            tax_code = item['taxTyCd']
            totals[tax_code] += item['taxblAmt']
            tax_totals[tax_code] += item['taxAmt']

        # Determine if this is a refund/return
        is_return = self.amount_total < 0
        rcpt_ty_cd = 'R' if is_return else 'S'

        # Payment type
        pmt_ty_cd = self._get_etims_payment_type()

        # Get eTIMS invoice number (must be a NUMBER per spec)
        etims_invc_no = self.etims_invoice_number or self._get_next_etims_invoice_number()

        # Handle refund fields - orgInvcNo should be the original's eTIMS invoice number
        if is_return:
            org_invc_no = 0
            if self.etims_original_order_id and self.etims_original_order_id.etims_invoice_number:
                org_invc_no = self.etims_original_order_id.etims_invoice_number

            rfd_dt = self._get_etims_date(self.date_order)
            rfd_rsn_cd = self.etims_refund_reason or '01'
        else:
            org_invc_no = 0
            rfd_dt = ''
            rfd_rsn_cd = ''

        # Customer info
        partner = self.partner_id
        cust_tin = partner.vat if partner else ''
        cust_nm = (partner.name if partner else 'Cash Sale')[:100]

        payload = {
            'trdInvcNo': (self.pos_reference or self.name or '')[:50],  # Trader invoice number (CHAR 50)
            'invcNo': etims_invc_no,  # eTIMS invoice number (NUMBER 38)
            'orgInvcNo': org_invc_no,
            'custTin': cust_tin,
            'custNm': cust_nm,
            'rcptTyCd': rcpt_ty_cd,
            'pmtTyCd': pmt_ty_cd,
            'salesSttsCd': '02',
            'cfmDt': self._get_etims_datetime(),
            'salesDt': self._get_etims_date(self.date_order),
            'stockRlsDt': self._get_etims_datetime(),
            'cnclReqDt': '',
            'cnclDt': '',
            'rfdDt': rfd_dt,
            'rfdRsnCd': rfd_rsn_cd,
            'totItemCnt': len(items),
            'taxblAmtA': round(totals['A'], 2),
            'taxblAmtB': round(totals['B'], 2),
            'taxblAmtC': round(totals['C'], 2),
            'taxblAmtD': round(totals['D'], 2),
            'taxblAmtE': round(totals['E'], 2),
            'taxRtA': 0,
            'taxRtB': 16,
            'taxRtC': 0,
            'taxRtD': 0,
            'taxRtE': 8,
            'taxAmtA': round(tax_totals['A'], 2),
            'taxAmtB': round(tax_totals['B'], 2),
            'taxAmtC': round(tax_totals['C'], 2),
            'taxAmtD': round(tax_totals['D'], 2),
            'taxAmtE': round(tax_totals['E'], 2),
            'totTaxblAmt': round(sum(totals.values()), 2),
            'totTaxAmt': round(sum(tax_totals.values()), 2),
            'totAmt': round(abs(self.amount_total), 2),
            'prchrAcptcYn': 'N',
            'remark': (self.note or '')[:400] if self.note else '',
            'regrId': self.env.user.login[:20] if self.env.user.login else 'admin',
            'regrNm': (self.env.user.name or 'Admin')[:60],
            'modrId': self.env.user.login[:20] if self.env.user.login else 'admin',
            'modrNm': (self.env.user.name or 'Admin')[:60],
            'receipt': {
                'custTin': cust_tin,
                'custMblNo': (partner.mobile or partner.phone or '') if partner else '',
                'rcptPbctDt': self._get_etims_datetime(),  # Receipt published datetime (CHAR 14)
                'trdeNm': cust_nm,
                'adrs': (partner.street or '')[:200] if partner else '',
                'topMsg': '',
                'btmMsg': '',
                'prchrAcptcYn': 'N',
            },
            'itemList': items,
        }

        return payload

    def _validate_etims_submission(self):
        """Validate that the POS order is ready for eTIMS submission."""
        self.ensure_one()

        if self.etims_submitted:
            return False  # Already submitted, not an error

        if self.state not in ('paid', 'done', 'invoiced'):
            return False  # Not ready yet

        # Validate products
        for line in self.lines:
            product = line.product_id
            if not product:
                continue

            if not product.product_tmpl_id.l10n_ke_etims_registered:
                raise UserError(_(
                    'Product "%s" must be registered with eTIMS before it can be sold.\n'
                    'Go to the product form and click "Register with eTIMS".'
                ) % product.name)

            if not product.product_tmpl_id.l10n_ke_item_class_id:
                raise UserError(_(
                    'Product "%s" is missing UNSPSC classification.\n'
                    'Go to the product form, eTIMS Kenya tab, and select a UNSPSC Classification.'
                ) % product.name)

        return True

    def _submit_to_etims(self):
        """Submit POS order to eTIMS."""
        self.ensure_one()

        # Get config
        try:
            config = self.env['etims.config'].get_config(self.company_id)
        except UserError:
            _logger.warning('eTIMS not configured for company %s', self.company_id.name)
            return False

        # Prepare and send
        payload = self._prepare_etims_payload()

        try:
            result = config._call_api('/saveTrnsSalesOsdc', payload)

            if result.get('resultCd') == '000':
                data = result.get('data', {})
                # Get SDC ID from config (set during device initialization)
                sdc_id = config.sdc_id if hasattr(config, 'sdc_id') else ''
                # Per OSCU spec: curRcptNo is the current receipt number
                rcpt_no = str(data.get('curRcptNo', data.get('rcptNo', '')))

                self.write({
                    'etims_submitted': True,
                    'etims_invoice_number': payload.get('invcNo'),  # Store the invoice number we sent
                    'etims_sdc_id': sdc_id,
                    'etims_rcpt_no': rcpt_no,
                    'etims_intrl_data': data.get('intrlData', ''),
                    'etims_rcpt_sign': data.get('rcptSign', ''),
                    'etims_sdc_datetime': data.get('sdcDateTime', ''),
                    'etims_submit_date': fields.Datetime.now(),
                    'etims_response': str(result),
                    'etims_submission_error': False,
                })
                _logger.info(
                    'POS Order %s submitted to eTIMS. Receipt #: %s',
                    self.name, rcpt_no
                )
                return True
            else:
                error_msg = result.get('resultMsg', 'Unknown error')
                self.write({
                    'etims_response': str(result),
                    'etims_submission_error': error_msg,
                })
                _logger.warning(
                    'POS Order %s eTIMS submission failed: %s',
                    self.name, error_msg
                )
                return False

        except Exception as e:
            self.etims_submission_error = str(e)
            _logger.error(
                'POS Order %s eTIMS submission error: %s',
                self.name, str(e)
            )
            return False

    def action_submit_etims(self):
        """Manual action to submit POS order to eTIMS."""
        self.ensure_one()

        if not self._validate_etims_submission():
            raise UserError(_('This order is not ready for eTIMS submission.'))

        if self._submit_to_etims():
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('POS Order submitted to eTIMS. Receipt #: %s') % self.etims_rcpt_no,
                    'type': 'success',
                }
            }
        else:
            raise UserError(_(
                'Failed to submit to eTIMS: %s'
            ) % (self.etims_submission_error or 'Unknown error'))

    def action_pos_order_paid(self):
        """
        Override to submit to eTIMS when POS order is paid.
        This is the key integration point - eTIMS submission happens at payment.
        """
        res = super().action_pos_order_paid()

        # Submit to eTIMS for Kenyan companies
        for order in self:
            if order._is_etims_applicable():
                try:
                    if order._validate_etims_submission():
                        order._submit_to_etims()
                except UserError as e:
                    # Don't block the POS transaction, log and continue
                    _logger.warning(
                        'eTIMS submission failed for POS order %s: %s',
                        order.name, str(e)
                    )
                    order.etims_submission_error = str(e)
                except Exception as e:
                    _logger.error(
                        'eTIMS submission error for POS order %s: %s',
                        order.name, str(e)
                    )
                    order.etims_submission_error = str(e)

        return res

    @api.model
    def _process_order(self, order, draft, existing_order):
        """
        Override to auto-link original order for POS returns.
        """
        # Check if this is a return order
        if order.get('lines'):
            for line_data in order['lines']:
                # line_data is a list of [command, id, vals]
                if isinstance(line_data, (list, tuple)) and len(line_data) > 2:
                    vals = line_data[2] if isinstance(line_data[2], dict) else {}
                    # Check for negative quantity (return)
                    if vals.get('qty', 0) < 0:
                        # This is a return - check for refunded_orderline_id
                        if vals.get('refunded_orderline_id'):
                            refunded_line = self.env['pos.order.line'].browse(vals['refunded_orderline_id'])
                            if refunded_line and refunded_line.order_id:
                                order['etims_original_order_id'] = refunded_line.order_id.id
                                if not order.get('etims_refund_reason'):
                                    order['etims_refund_reason'] = '01'  # Default reason
                        break

        return super()._process_order(order, draft, existing_order)


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    def _get_etims_tax_code(self):
        """Get eTIMS tax code for this order line."""
        product = self.product_id
        if product and product.product_tmpl_id.l10n_ke_tax_type:
            return product.product_tmpl_id.l10n_ke_tax_type

        # Fallback to tax amount detection
        tax = self.tax_ids[:1] if self.tax_ids else None
        if not tax:
            return 'D'

        amount = tax.amount if tax else 0
        if amount == 16:
            return 'B'
        elif amount == 8:
            return 'E'
        elif amount == 0:
            return 'C'
        return 'D'
