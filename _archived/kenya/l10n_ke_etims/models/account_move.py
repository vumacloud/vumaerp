# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # eTIMS Fields
    etims_submitted = fields.Boolean(
        string='Submitted to eTIMS',
        default=False,
        copy=False,
        tracking=True,
    )
    etims_receipt_number = fields.Char(
        string='eTIMS Receipt Number',
        copy=False,
        readonly=True,
    )
    etims_internal_data = fields.Char(
        string='eTIMS Internal Data',
        copy=False,
        readonly=True,
    )
    etims_receipt_signature = fields.Char(
        string='eTIMS Receipt Signature',
        copy=False,
        readonly=True,
    )
    etims_sdc_id = fields.Char(
        string='SDC ID',
        copy=False,
        readonly=True,
    )
    etims_sdc_datetime = fields.Datetime(
        string='SDC DateTime',
        copy=False,
        readonly=True,
    )
    etims_mrc_no = fields.Char(
        string='MRC Number',
        copy=False,
        readonly=True,
    )
    etims_qr_code = fields.Binary(
        string='eTIMS QR Code',
        copy=False,
        readonly=True,
    )
    etims_submit_date = fields.Datetime(
        string='eTIMS Submit Date',
        copy=False,
        readonly=True,
    )
    etims_error_message = fields.Text(
        string='eTIMS Error',
        copy=False,
        readonly=True,
    )
    etims_transaction_type = fields.Selection([
        ('01', 'Copy'),
        ('02', 'Normal'),
        ('03', 'Trained'),
        ('04', 'Proforma'),
    ], string='Transaction Type', default='02')

    etims_sale_type = fields.Selection([
        ('N', 'Normal Sale'),
        ('C', 'Credit Sale'),
    ], string='Sale Type', default='N')

    etims_receipt_type = fields.Selection([
        ('S', 'Sale'),
        ('R', 'Refund'),
    ], string='Receipt Type', compute='_compute_etims_receipt_type', store=True)

    @api.depends('move_type')
    def _compute_etims_receipt_type(self):
        for move in self:
            if move.move_type in ('out_refund', 'in_refund'):
                move.etims_receipt_type = 'R'
            else:
                move.etims_receipt_type = 'S'

    def action_view_etims_details(self):
        """View eTIMS submission details."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('eTIMS Details'),
            'res_model': 'account.move',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {'active_tab': 'etims'},
        }

    def action_submit_to_etims(self):
        """Submit invoice to KRA eTIMS."""
        self.ensure_one()

        if self.etims_submitted:
            raise UserError(_('This invoice has already been submitted to eTIMS.'))

        if self.state != 'posted':
            raise UserError(_('Only posted invoices can be submitted to eTIMS.'))

        if self.move_type not in ('out_invoice', 'out_refund'):
            raise UserError(_('Only customer invoices and credit notes can be submitted to eTIMS.'))

        # Get eTIMS configuration
        config = self.env['etims.config'].get_active_config()
        if not config:
            raise UserError(_('eTIMS is not configured. Please configure eTIMS settings first.'))

        api = self.env['etims.api']

        # Prepare invoice data
        invoice_data = self._prepare_etims_invoice_data(config)

        try:
            # Submit to eTIMS
            response = api.save_sales(config, invoice_data)

            if response.get('resultCd') == '000':
                # Success
                result_data = response.get('data', {})
                self.write({
                    'etims_submitted': True,
                    'etims_receipt_number': result_data.get('rcptNo'),
                    'etims_internal_data': result_data.get('intrlData'),
                    'etims_receipt_signature': result_data.get('rcptSign'),
                    'etims_sdc_id': result_data.get('sdcId'),
                    'etims_sdc_datetime': result_data.get('sdcDateTime'),
                    'etims_mrc_no': result_data.get('mrcNo'),
                    'etims_submit_date': fields.Datetime.now(),
                    'etims_error_message': False,
                })
                self.message_post(body=_('Invoice successfully submitted to eTIMS. Receipt: %s') % result_data.get('rcptNo'))
                return True
            else:
                # Error
                error_msg = response.get('resultMsg', 'Unknown error')
                self.write({
                    'etims_error_message': error_msg,
                })
                raise UserError(_('eTIMS Error: %s') % error_msg)

        except Exception as e:
            _logger.error('eTIMS submission error: %s', str(e))
            self.write({
                'etims_error_message': str(e),
            })
            raise UserError(_('Failed to submit to eTIMS: %s') % str(e))

    def _prepare_etims_invoice_data(self, config):
        """Prepare invoice data for eTIMS API."""
        self.ensure_one()

        # Get customer info
        partner = self.partner_id
        customer_pin = partner.vat or partner.etims_pin or ''
        customer_name = partner.name or ''

        # Prepare line items
        items = []
        for idx, line in enumerate(self.invoice_line_ids.filtered(lambda l: l.display_type == 'product'), 1):
            product = line.product_id

            # Get item classification
            item_cls = product.etims_item_class_id.code if product.etims_item_class_id else ''

            # Get tax info
            tax_type = 'B'  # Default VAT
            tax_rate = 16.0  # Default Kenya VAT
            if line.tax_ids:
                tax = line.tax_ids[0]
                tax_rate = abs(tax.amount)
                if tax.amount == 0:
                    tax_type = 'E'  # Exempt
                elif tax.amount == 16:
                    tax_type = 'B'  # Standard VAT
                elif tax.amount == 8:
                    tax_type = 'C'  # Reduced rate

            item_data = {
                'itemSeq': idx,
                'itemCd': product.default_code or str(product.id),
                'itemClsCd': item_cls,
                'itemNm': line.name or product.name,
                'pkgUnitCd': product.etims_pkg_unit_code or 'NT',
                'pkg': line.quantity,
                'qtyUnitCd': product.etims_qty_unit_code or 'U',
                'qty': line.quantity,
                'prc': line.price_unit,
                'splyAmt': line.price_subtotal,
                'dcRt': line.discount or 0,
                'dcAmt': (line.price_unit * line.quantity * (line.discount / 100)) if line.discount else 0,
                'taxTyCd': tax_type,
                'taxAmt': line.price_total - line.price_subtotal,
                'totAmt': line.price_total,
            }
            items.append(item_data)

        # Calculate totals by tax type
        tax_totals = self._calculate_etims_tax_totals()

        data = {
            'tin': config.tin,
            'bhfId': config.branch_id or '00',
            'invcNo': self.name,
            'orgInvcNo': self.reversed_entry_id.etims_receipt_number if self.reversed_entry_id else None,
            'custTin': customer_pin,
            'custNm': customer_name,
            'salesTyCd': self.etims_sale_type,
            'rcptTyCd': self.etims_receipt_type,
            'pmtTyCd': '01',  # Default to cash
            'salesSttsCd': '02',  # Approved
            'cfmDt': self.invoice_date.strftime('%Y%m%d%H%M%S') if self.invoice_date else '',
            'salesDt': self.invoice_date.strftime('%Y%m%d') if self.invoice_date else '',
            'stockRlsDt': self.invoice_date.strftime('%Y%m%d%H%M%S') if self.invoice_date else '',
            'totItemCnt': len(items),
            'taxblAmtA': tax_totals.get('A', {}).get('taxable', 0),
            'taxblAmtB': tax_totals.get('B', {}).get('taxable', 0),
            'taxblAmtC': tax_totals.get('C', {}).get('taxable', 0),
            'taxblAmtD': tax_totals.get('D', {}).get('taxable', 0),
            'taxblAmtE': tax_totals.get('E', {}).get('taxable', 0),
            'taxRtA': 0,
            'taxRtB': 16,
            'taxRtC': 8,
            'taxRtD': 0,
            'taxRtE': 0,
            'taxAmtA': tax_totals.get('A', {}).get('tax', 0),
            'taxAmtB': tax_totals.get('B', {}).get('tax', 0),
            'taxAmtC': tax_totals.get('C', {}).get('tax', 0),
            'taxAmtD': tax_totals.get('D', {}).get('tax', 0),
            'taxAmtE': tax_totals.get('E', {}).get('tax', 0),
            'totTaxblAmt': self.amount_untaxed,
            'totTaxAmt': self.amount_tax,
            'totAmt': self.amount_total,
            'remark': self.narration or '',
            'itemList': items,
        }

        return data

    def _calculate_etims_tax_totals(self):
        """Calculate tax totals by eTIMS tax type."""
        totals = {}
        for line in self.invoice_line_ids.filtered(lambda l: l.display_type == 'product'):
            tax_type = 'B'  # Default
            if line.tax_ids:
                tax = line.tax_ids[0]
                if tax.amount == 0:
                    tax_type = 'E'
                elif tax.amount == 16:
                    tax_type = 'B'
                elif tax.amount == 8:
                    tax_type = 'C'

            if tax_type not in totals:
                totals[tax_type] = {'taxable': 0, 'tax': 0}

            totals[tax_type]['taxable'] += line.price_subtotal
            totals[tax_type]['tax'] += line.price_total - line.price_subtotal

        return totals

    def action_post(self):
        """Override to auto-submit to eTIMS if configured."""
        res = super().action_post()

        # Check for auto-submission
        for move in self:
            if move.move_type in ('out_invoice', 'out_refund'):
                config = self.env['etims.config'].get_active_config()
                if config and config.auto_submit_invoices:
                    try:
                        move.action_submit_to_etims()
                    except Exception as e:
                        _logger.warning('Auto eTIMS submission failed: %s', str(e))

        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    etims_item_code = fields.Char(
        string='eTIMS Item Code',
        related='product_id.etims_item_code',
        readonly=True,
    )
