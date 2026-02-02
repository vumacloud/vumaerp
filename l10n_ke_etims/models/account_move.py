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
    etims_scu_no = fields.Char(string='SCU No', copy=False, readonly=True,
                               help='Signed Code Unit number from KRA')
    etims_rcpt_no = fields.Char(string='Receipt No', copy=False, readonly=True)
    etims_intrl_data = fields.Char(string='Internal Data', copy=False, readonly=True)
    etims_rcpt_sign = fields.Char(string='Receipt Signature', copy=False, readonly=True)
    etims_submit_date = fields.Datetime(string='eTIMS Submit Date', copy=False, readonly=True)
    etims_response = fields.Text(string='eTIMS Response', copy=False, readonly=True)

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
        tax = line.tax_ids[:1] if line.tax_ids else None
        tax_code = self._get_etims_tax_code(tax)
        tax_amt = tax.amount if tax else 0

        unit_price = line.price_unit
        qty = line.quantity
        discount_amt = (line.price_unit * line.quantity * line.discount / 100) if line.discount else 0
        supply_amt = (unit_price * qty) - discount_amt

        # Calculate tax
        if tax_amt > 0:
            taxable_amt = supply_amt / (1 + tax_amt / 100)
            tax_amount = supply_amt - taxable_amt
        else:
            taxable_amt = supply_amt
            tax_amount = 0

        return {
            'itemSeq': seq,
            'itemCd': line.product_id.default_code or str(line.product_id.id) if line.product_id else 'SVC',
            'itemClsCd': '5020299',  # Default classification - should be configurable
            'itemNm': (line.name or line.product_id.name or 'Item')[:200],
            'pkgUnitCd': 'NT',  # Package unit: NT=Not Applicable
            'pkg': 1,
            'qtyUnitCd': 'U',  # Quantity unit: U=Unit
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

        payload = {
            'invcNo': self.name or '',
            'orgInvcNo': 0,  # Original invoice for refunds
            'custTin': self.partner_id.vat or '',
            'custNm': (self.partner_id.name or 'Cash Customer')[:100],
            'salesTyCd': 'N',  # N=Normal, C=Copy
            'rcptTyCd': rcpt_ty_cd,
            'pmtTyCd': pmt_ty_cd,
            'salesSttsCd': '02',  # 02=Approved
            'cfmDt': self._get_etims_datetime(),
            'salesDt': self._get_etims_date(self.invoice_date),
            'stockRlsDt': self._get_etims_datetime(),
            'cnclReqDt': '',
            'cnclDt': '',
            'rfdDt': '' if rcpt_ty_cd == 'S' else self._get_etims_date(),
            'rfdRsnCd': '' if rcpt_ty_cd == 'S' else '01',
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
                'rptNo': 0,
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

        # Get config
        config = self.env['etims.config'].get_config(self.company_id)

        # Prepare and send
        payload = self._prepare_etims_payload()
        result = config._call_api('/trnsSales/saveSalesWr', payload)

        # Process response
        if result.get('resultCd') == '000':
            data = result.get('data', {})
            self.write({
                'etims_submitted': True,
                'etims_scu_no': data.get('scuNo'),
                'etims_rcpt_no': str(data.get('rcptNo', '')),
                'etims_intrl_data': data.get('intrlData'),
                'etims_rcpt_sign': data.get('rcptSign'),
                'etims_submit_date': fields.Datetime.now(),
                'etims_response': str(result),
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Invoice submitted to eTIMS. SCU: %s') % data.get('scuNo'),
                    'type': 'success',
                }
            }
        else:
            error_msg = result.get('resultMsg', 'Unknown error')
            self.etims_response = str(result)
            raise UserError(_('eTIMS Error: %s') % error_msg)
