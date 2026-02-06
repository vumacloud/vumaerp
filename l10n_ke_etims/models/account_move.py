# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # eTIMS Fields
    etims_submitted = fields.Boolean(string='Submitted to eTIMS', copy=False)
    etims_invoice_number = fields.Integer(
        string='eTIMS Invoice Number',
        copy=False,
        readonly=True,
        help='Sequential numeric invoice number for eTIMS (invcNo)'
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

    etims_cu_invoice_number = fields.Char(
        string='CU Invoice Number',
        copy=False,
        readonly=True,
        compute='_compute_etims_cu_invoice_number',
        store=True,
        help='Formatted CU Invoice Number: {CU_ID}/{Receipt_Number}'
    )
    etims_sdc_id = fields.Char(string='SDC ID', copy=False, readonly=True,
                               help='SDC/CU ID from device initialization')
    etims_rcpt_no = fields.Char(string='Receipt No', copy=False, readonly=True)
    etims_intrl_data = fields.Char(string='Internal Data', copy=False, readonly=True)
    etims_rcpt_sign = fields.Char(string='Receipt Signature', copy=False, readonly=True)
    etims_sdc_datetime = fields.Char(string='SDC DateTime', copy=False, readonly=True,
                                     help='Date/time from OSCU/VSCU')
    etims_submit_date = fields.Datetime(string='eTIMS Submit Date', copy=False, readonly=True)
    etims_response = fields.Text(string='eTIMS Response', copy=False, readonly=True)

    # QR Code
    etims_qr_code = fields.Binary(
        string='eTIMS QR Code',
        compute='_compute_etims_qr_code',
        help='QR code for receipt per TIS spec'
    )

    @api.depends('etims_transaction_type', 'move_type')
    def _compute_etims_receipt_type_label(self):
        """Compute receipt type label per TIS spec Section 4."""
        for move in self:
            if move.move_type == 'out_refund':
                receipt_type = 'CREDIT_NOTE'
            else:
                receipt_type = 'SALES'

            trans_type = move.etims_transaction_type or 'NORMAL'

            labels = {
                ('NORMAL', 'SALES'): 'NS',
                ('NORMAL', 'CREDIT_NOTE'): 'NC',
                ('COPY', 'SALES'): 'CS',
                ('COPY', 'CREDIT_NOTE'): 'CC',
                ('TRAINING', 'SALES'): 'TS',
                ('TRAINING', 'CREDIT_NOTE'): 'TC',
                ('PROFORMA', 'SALES'): 'PS',
            }
            move.etims_receipt_type_label = labels.get((trans_type, receipt_type), 'NS')

    @api.depends('etims_submitted', 'etims_sdc_datetime', 'etims_sdc_id', 'etims_rcpt_no',
                 'etims_intrl_data', 'etims_rcpt_sign')
    def _compute_etims_qr_code(self):
        """Generate QR code image per TIS spec."""
        import base64
        for move in self:
            if not move.etims_submitted:
                move.etims_qr_code = False
                continue

            # Get QR image from mixin
            qr_base64 = move.get_etims_qr_image()
            if qr_base64:
                move.etims_qr_code = qr_base64
            else:
                move.etims_qr_code = False

    @api.depends('etims_sdc_id', 'etims_rcpt_no')
    def _compute_etims_cu_invoice_number(self):
        """Compute CU Invoice Number in format: {CU_ID}/{Receipt_Number}"""
        for move in self:
            if move.etims_sdc_id and move.etims_rcpt_no:
                move.etims_cu_invoice_number = f"{move.etims_sdc_id}/{move.etims_rcpt_no}"
            else:
                move.etims_cu_invoice_number = False

    def _get_next_etims_invoice_number(self):
        """
        Get the next sequential eTIMS invoice number.
        Per OSCU spec, invcNo must be a NUMBER (integer sequence).

        Uses PostgreSQL advisory lock to prevent race conditions when
        multiple invoices are submitted simultaneously.
        """
        self.ensure_one()
        # Acquire advisory lock for this company's invoice number sequence
        # Uses a hash of 'etims_invc_no_{company_id}' as the lock key
        self.env.cr.execute(
            "SELECT pg_advisory_xact_lock(hashtext(%s))",
            (f'etims_invc_no_{self.company_id.id}',)
        )
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

    def _prepare_etims_item(self, line, seq):
        """Prepare a single invoice line for eTIMS."""
        product = line.product_id
        product_tmpl = product.product_tmpl_id if product else None

        # Get tax information - prefer product's eTIMS tax type, fallback to line tax
        tax = line.tax_ids[:1] if line.tax_ids else None
        if product_tmpl and product_tmpl.l10n_ke_tax_type:
            tax_code = product_tmpl.l10n_ke_tax_type
        else:
            tax_code = self._get_etims_tax_code(tax)

        tax_amt = tax.amount if tax else 0
        tax_is_inclusive = tax.price_include if tax else True

        unit_price = line.price_unit
        qty = line.quantity
        discount_amt = (line.price_unit * line.quantity * line.discount / 100) if line.discount else 0
        supply_amt = (unit_price * qty) - discount_amt

        # Calculate tax - handle both inclusive and exclusive pricing for B2B support
        if tax_amt > 0:
            if tax_is_inclusive:
                # Tax-inclusive: price already includes tax, extract taxable amount
                taxable_amt = supply_amt / (1 + tax_amt / 100)
                tax_amount = supply_amt - taxable_amt
            else:
                # Tax-exclusive: price is net, calculate tax to add
                taxable_amt = supply_amt
                tax_amount = supply_amt * tax_amt / 100
                # For eTIMS, supply_amt should be the gross amount
                supply_amt = taxable_amt + tax_amount
        else:
            taxable_amt = supply_amt
            tax_amount = 0

        # Get item code - use eTIMS item code if registered, else default_code
        if product:
            item_code = product._get_etims_item_code()[:20]
        else:
            item_code = 'SVC'

        # Get UNSPSC classification code from product
        if product:
            item_class_code = product._get_etims_item_class_code()
        else:
            item_class_code = ''

        # Get unit codes from product
        if product:
            unit_codes = product._get_etims_unit_codes()
            pkg_unit_code = unit_codes['pkg_unit']
            qty_unit_code = unit_codes['qty_unit']
        else:
            pkg_unit_code = 'NT'
            qty_unit_code = 'U'

        return {
            'itemSeq': seq,
            'itemCd': item_code,
            'itemClsCd': item_class_code,
            'itemNm': (line.name or (product.name if product else 'Item'))[:200],
            'pkgUnitCd': pkg_unit_code,
            'pkg': 1,
            'qtyUnitCd': qty_unit_code,
            'qty': qty,
            'prc': round(unit_price, 2),
            'splyAmt': round(supply_amt, 2),
            'dcRt': line.discount or 0,
            'dcAmt': round(discount_amt, 2),
            'taxTyCd': tax_code,
            'taxblAmt': round(taxable_amt, 2),
            'taxAmt': round(tax_amount, 2),
            'totAmt': round(supply_amt, 2),
        }

    def _prepare_etims_payload(self):
        """Prepare the full eTIMS sales transaction payload."""
        self.ensure_one()

        if self.move_type not in ('out_invoice', 'out_refund'):
            raise UserError(_('Only customer invoices can be submitted to eTIMS.'))

        # Prepare items
        items = []
        totals = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
        tax_totals = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}

        seq = 0
        for line in self.invoice_line_ids.filtered(lambda l: not l.display_type):
            seq += 1
            item = self._prepare_etims_item(line, seq)
            items.append(item)

            # Accumulate totals by tax type
            tax_code = item['taxTyCd']
            totals[tax_code] += item['taxblAmt']
            tax_totals[tax_code] += item['taxAmt']

        # Receipt type: S=Sale, R=Refund
        rcpt_ty_cd = 'R' if self.move_type == 'out_refund' else 'S'

        # Payment type (simplified - could be enhanced)
        pmt_ty_cd = '01'  # 01=Cash, 02=Credit, 03=Cash/Credit, etc.

        # Get eTIMS invoice number (must be a NUMBER per spec)
        etims_invc_no = self.etims_invoice_number or self._get_next_etims_invoice_number()

        # Handle original invoice number for credit notes
        org_invc_no = 0
        if self.move_type == 'out_refund' and self.reversed_entry_id:
            # Get the original invoice's eTIMS invoice number
            if self.reversed_entry_id.etims_invoice_number:
                org_invc_no = self.reversed_entry_id.etims_invoice_number

        # Get refund reason code (per OSCU spec Section 4.16: 01-05 only)
        rfd_rsn_cd = ''
        if self.move_type == 'out_refund':
            # Map to valid KRA codes: 01=Return, 02=Incorrect info, 03=Omission, 04=Cancellation, 05=Other
            if hasattr(self, 'etims_refund_reason') and self.etims_refund_reason:
                reason = self.etims_refund_reason
                # Map old codes to new spec-compliant codes
                reason_map = {
                    '01': '01',  # Damage/Defect -> Return
                    '02': '05',  # Change of Mind -> Other
                    '03': '02',  # Wrong Item -> Incorrect info
                    '04': '05',  # Late Delivery -> Other
                    '05': '05',  # Duplicate -> Other
                    '06': '02',  # Price Dispute -> Incorrect info
                    '07': '03',  # Quantity Dispute -> Omission
                    '08': '01',  # Quality Issues -> Return
                    '09': '04',  # Cancellation -> Cancellation
                    '10': '05',  # Other -> Other
                }
                rfd_rsn_cd = reason_map.get(reason, '05')
            else:
                rfd_rsn_cd = '01'

        payload = {
            'trdInvcNo': (self.name or '')[:50],  # Trader invoice number (CHAR 50)
            'invcNo': etims_invc_no,  # eTIMS invoice number (NUMBER 38)
            'orgInvcNo': org_invc_no,  # Original invoice for refunds
            'custTin': self.partner_id.vat or '',
            'custNm': (self.partner_id.name or 'Cash Customer')[:100],
            'rcptTyCd': rcpt_ty_cd,
            'pmtTyCd': pmt_ty_cd,
            'salesSttsCd': '02',  # 02=Approved
            'cfmDt': self._get_etims_datetime(),
            'salesDt': self._get_etims_date(self.invoice_date),
            'stockRlsDt': self._get_etims_datetime(),
            'cnclReqDt': '',
            'cnclDt': '',
            'rfdDt': '' if rcpt_ty_cd == 'S' else self._get_etims_date(),
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
            'totAmt': round(self.amount_total, 2),
            'prchrAcptcYn': 'N',
            'remark': (self.narration or '')[:400],
            'regrId': self.env.user.login[:20] if self.env.user.login else 'admin',
            'regrNm': (self.env.user.name or 'Admin')[:60],
            'modrId': self.env.user.login[:20] if self.env.user.login else 'admin',
            'modrNm': (self.env.user.name or 'Admin')[:60],
            'receipt': {
                'custTin': self.partner_id.vat or '',
                'custMblNo': self.partner_id.mobile or self.partner_id.phone or '',
                'rcptPbctDt': self._get_etims_datetime(),  # Receipt published datetime (CHAR 14, YYYYMMDDHHmmss)
                'trdeNm': (self.partner_id.name or '')[:100],
                'adrs': (self.partner_id.street or '')[:200],
                'topMsg': '',
                'btmMsg': '',
                'prchrAcptcYn': 'N',
            },
            'itemList': items,
        }

        return payload

    def action_submit_etims(self):
        """Submit invoice to eTIMS."""
        self.ensure_one()

        if self.etims_submitted:
            raise UserError(_('This invoice has already been submitted to eTIMS.'))

        if self.state != 'posted':
            raise UserError(_('Only posted invoices can be submitted to eTIMS.'))

        # For credit notes, validate that the original invoice was submitted to eTIMS
        if self.move_type == 'out_refund' and self.reversed_entry_id:
            if not self.reversed_entry_id.etims_submitted:
                raise UserError(_(
                    'Cannot submit this credit note to eTIMS because the original '
                    'invoice (%s) has not been submitted yet.\n\n'
                    'Please submit the original invoice to eTIMS first, then submit this credit note.'
                ) % self.reversed_entry_id.name)

        # Validate products are registered with eTIMS and have UNSPSC codes
        product_lines = self.invoice_line_ids.filtered(
            lambda l: not l.display_type and l.product_id
        )

        # Check for unregistered products
        unregistered = product_lines.filtered(
            lambda l: not l.product_id.product_tmpl_id.l10n_ke_etims_registered
        )
        if unregistered:
            product_names = ', '.join(unregistered.mapped('product_id.name')[:5])
            raise UserError(_(
                'The following products must be registered with eTIMS before submitting the invoice:\n%s'
                '\n\nGo to the product form and click "Register with eTIMS".'
            ) % product_names)

        # Check for missing UNSPSC classifications
        missing_unspsc = product_lines.filtered(
            lambda l: not l.product_id.product_tmpl_id.l10n_ke_item_class_id
        )
        if missing_unspsc:
            product_names = ', '.join(missing_unspsc.mapped('product_id.name')[:5])
            raise UserError(_(
                'The following products are missing UNSPSC classification:\n%s'
                '\n\nGo to the product form, eTIMS Kenya tab, and select a UNSPSC Classification.'
            ) % product_names)

        # Get config and verify OSCU connection
        config = self.env['etims.config'].get_config(self.company_id)
        config.check_connection()  # OSCU Connection Guard - raises if not ready

        # Prepare and send
        payload = self._prepare_etims_payload()
        result = config._call_api('/saveTrnsSalesOsdc', payload)

        # Process response per OSCU spec TrnsSalesSaveWrRes
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
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Invoice submitted to eTIMS. Receipt #: %s') % rcpt_no,
                    'type': 'success',
                }
            }
        else:
            error_msg = result.get('resultMsg', 'Unknown error')
            self.etims_response = str(result)
            raise UserError(_('eTIMS Error: %s') % error_msg)
