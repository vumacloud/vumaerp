# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import json
import base64
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # EFRIS Fields
    efris_submitted = fields.Boolean(
        string='Submitted to EFRIS',
        default=False,
        copy=False,
        readonly=True,
    )
    efris_fdn = fields.Char(
        string='Fiscal Document Number',
        copy=False,
        readonly=True,
        help='Fiscal Document Number assigned by URA EFRIS',
    )
    efris_verification_code = fields.Char(
        string='Verification Code',
        copy=False,
        readonly=True,
    )
    efris_qr_code = fields.Binary(
        string='EFRIS QR Code',
        copy=False,
        readonly=True,
    )
    efris_submission_date = fields.Datetime(
        string='EFRIS Submission Date',
        copy=False,
        readonly=True,
    )
    efris_status = fields.Selection([
        ('not_submitted', 'Not Submitted'),
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], string='EFRIS Status', default='not_submitted', copy=False, readonly=True)

    efris_error_message = fields.Text(
        string='EFRIS Error',
        copy=False,
        readonly=True,
    )
    efris_response = fields.Text(
        string='EFRIS Response',
        copy=False,
        readonly=True,
    )

    # Original invoice reference for credit notes
    efris_original_fdn = fields.Char(
        string='Original FDN',
        help='FDN of original invoice (for credit notes)',
    )

    # Buyer information
    efris_buyer_tin = fields.Char(
        string='Buyer TIN',
        help='Buyer Taxpayer Identification Number',
    )
    efris_buyer_legal_name = fields.Char(
        string='Buyer Legal Name',
    )
    efris_buyer_type = fields.Selection([
        ('0', 'Business (B2B)'),
        ('1', 'Individual (B2C)'),
        ('2', 'Government'),
        ('3', 'Foreigner'),
    ], string='Buyer Type', default='0')

    def _get_efris_config(self):
        """Get EFRIS configuration for current company."""
        config = self.env['efris.config'].search([
            ('company_id', '=', self.company_id.id),
            ('active', '=', True),
        ], limit=1)

        if not config:
            raise UserError(_(
                "No EFRIS configuration found for company %s. "
                "Please configure EFRIS settings first."
            ) % self.company_id.name)

        return config

    def _prepare_efris_invoice_lines(self):
        """Prepare invoice lines for EFRIS submission."""
        lines = []
        for idx, line in enumerate(self.invoice_line_ids.filtered(lambda l: not l.display_type), 1):
            tax_code = '01'  # Default standard VAT
            tax_rate = 18.0  # Uganda VAT rate

            if line.tax_ids:
                # Get first tax
                tax = line.tax_ids[0]
                efris_code = self.env['efris.tax.code'].get_tax_code(tax)
                if efris_code:
                    tax_code = efris_code
                tax_rate = abs(tax.amount)

            lines.append({
                "item": str(idx),
                "itemCode": line.product_id.default_code or "",
                "itemName": line.name or line.product_id.name,
                "qty": str(line.quantity),
                "unitOfMeasure": line.product_uom_id.name or "PCE",
                "unitPrice": str(round(line.price_unit, 2)),
                "total": str(round(line.price_subtotal, 2)),
                "taxRate": str(tax_rate),
                "tax": str(round(line.price_total - line.price_subtotal, 2)),
                "discountTotal": str(round((line.price_unit * line.quantity * line.discount / 100), 2)),
                "discountTaxRate": str(tax_rate),
                "orderNumber": "",
                "discountFlag": "2" if line.discount > 0 else "0",
                "deemedFlag": "2",
                "exciseFlag": "2",
                "categoryId": "",
                "categoryName": "",
                "goodsCategoryId": line.product_id.efris_goods_code or "",
                "goodsCategoryName": "",
                "exciseRate": "",
                "exciseRule": "",
                "exciseTax": "",
                "pack": "",
                "stick": "",
                "exciseUnit": "",
                "exciseCurrency": "",
                "exciseRateName": "",
            })

        return lines

    def _prepare_efris_payload(self):
        """Prepare the full EFRIS invoice payload."""
        self.ensure_one()

        config = self._get_efris_config()

        # Determine document type
        doc_type = self.env['efris.document.type'].get_document_type_code(self.move_type)

        # Prepare line items
        goods_details = self._prepare_efris_invoice_lines()

        # Calculate totals
        tax_amount = sum(line.get('tax', 0) for line in goods_details)

        payload = {
            "sellerDetails": {
                "tin": config.tin,
                "ninBrn": "",
                "legalName": self.company_id.name,
                "businessName": self.company_id.name,
                "address": self.company_id.street or "",
                "mobilePhone": self.company_id.phone or "",
                "linePhone": "",
                "emailAddress": self.company_id.email or "",
                "placeOfBusiness": self.company_id.city or "",
                "referenceNo": "",
                "branchId": "",
                "isCheckReferenceNo": ""
            },
            "basicInformation": {
                "invoiceNo": self.name,
                "antifakeCode": "",
                "deviceNo": config.device_no,
                "issuedDate": self.invoice_date.strftime("%Y-%m-%d") if self.invoice_date else datetime.now().strftime("%Y-%m-%d"),
                "issuedTime": datetime.now().strftime("%H:%M:%S"),
                "operator": self.env.user.name,
                "currency": self.currency_id.name,
                "oriInvoiceId": self.efris_original_fdn or "",
                "invoiceType": doc_type,
                "invoiceIndustryCode": "101",
                "branchId": ""
            },
            "buyerDetails": {
                "buyerTin": self.efris_buyer_tin or self.partner_id.vat or "",
                "buyerNinBrn": "",
                "buyerPassportNum": "",
                "buyerLegalName": self.efris_buyer_legal_name or self.partner_id.name,
                "buyerBusinessName": self.partner_id.name,
                "buyerAddress": self.partner_id.street or "",
                "buyerEmail": self.partner_id.email or "",
                "buyerMobilePhone": self.partner_id.phone or "",
                "buyerLinePhone": "",
                "buyerPlaceOfBusi": self.partner_id.city or "",
                "buyerType": self.efris_buyer_type or "0",
                "buyerCitizenship": self.partner_id.country_id.code or "UG",
                "buyerSector": "1",
                "buyerReferenceNo": self.partner_id.ref or ""
            },
            "goodsDetails": goods_details,
            "taxDetails": [
                {
                    "taxCategoryCode": "01",
                    "netAmount": str(round(self.amount_untaxed, 2)),
                    "taxRate": "18",
                    "taxAmount": str(round(self.amount_tax, 2)),
                    "grossAmount": str(round(self.amount_total, 2)),
                    "exciseUnit": "",
                    "exciseCurrency": "",
                    "taxRateName": "Standard"
                }
            ],
            "summary": {
                "netAmount": str(round(self.amount_untaxed, 2)),
                "taxAmount": str(round(self.amount_tax, 2)),
                "grossAmount": str(round(self.amount_total, 2)),
                "itemCount": str(len(goods_details)),
                "modeCode": "0",
                "remarks": self.narration or "",
                "qrCode": ""
            },
            "payWay": [
                {
                    "paymentMode": "101",
                    "paymentAmount": str(round(self.amount_total, 2)),
                    "orderNumber": ""
                }
            ],
            "extend": {}
        }

        return payload

    def action_submit_to_efris(self):
        """Submit invoice to EFRIS."""
        self.ensure_one()

        if self.efris_submitted:
            raise UserError(_("This invoice has already been submitted to EFRIS."))

        if self.state != 'posted':
            raise UserError(_("Only posted invoices can be submitted to EFRIS."))

        if self.move_type not in ['out_invoice', 'out_refund']:
            raise UserError(_("Only customer invoices and credit notes can be submitted to EFRIS."))

        config = self._get_efris_config()

        # Prepare payload
        payload = self._prepare_efris_payload()

        self.write({
            'efris_status': 'pending',
            'efris_error_message': False,
        })

        try:
            # Submit to EFRIS
            result = config._send_request("T104", payload)

            # Parse response
            data = result.get('data', {})
            if data.get('content'):
                response_content = json.loads(
                    base64.b64decode(data['content']).decode()
                )

                self.write({
                    'efris_submitted': True,
                    'efris_fdn': response_content.get('basicInformation', {}).get('invoiceId'),
                    'efris_verification_code': response_content.get('basicInformation', {}).get('antifakeCode'),
                    'efris_status': 'accepted',
                    'efris_submission_date': fields.Datetime.now(),
                    'efris_response': json.dumps(response_content, indent=2),
                })

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Invoice submitted to EFRIS successfully. FDN: %s') % self.efris_fdn,
                        'type': 'success',
                        'sticky': False,
                    }
                }

        except UserError as e:
            self.write({
                'efris_status': 'rejected',
                'efris_error_message': str(e),
            })
            raise

    def action_view_efris_response(self):
        """View EFRIS API response."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('EFRIS Response'),
            'res_model': 'account.move',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('l10n_ug_efris.view_move_efris_response_form').id,
            'target': 'new',
        }


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    efris_goods_code = fields.Char(
        string='EFRIS Goods Code',
        related='product_id.efris_goods_code',
        store=True,
    )
