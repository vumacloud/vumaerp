# -*- coding: utf-8 -*-
"""
eTIMS Receipt Formatting and QR Code Generation

Per TIS Technical Specifications v2.0, Section 6.23:
- Receipt must include formatted internal data and signature
- QR code format: date#time#cu_number#receipt_number#internal_data#signature
- Data should be dash-separated after every 4th character
"""
import base64
import io
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

# Try to import qrcode library
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False
    _logger.warning('qrcode library not installed. QR code generation will be disabled.')


class EtimsReceiptMixin(models.AbstractModel):
    """
    Mixin providing eTIMS receipt formatting utilities.

    Per TIS spec Section 6.23.8:
    - Internal data and signature must be formatted with dashes after every 4th character
    - QR code must contain: date#time#cu_number#receipt_number#internal_data#signature
    """
    _name = 'etims.receipt.mixin'
    _description = 'eTIMS Receipt Formatting Mixin'

    @api.model
    def format_with_dashes(self, data, group_size=4):
        """
        Format data string with dashes after every Nth character.

        Per TIS spec Section 6.23:
        Internal data and receipt signature should be separated by dash
        after every 4th character for readability.

        Args:
            data: String to format
            group_size: Characters per group (default 4)

        Returns:
            Formatted string with dashes (e.g., "ABCD-EFGH-IJKL")
        """
        if not data:
            return ''

        # Remove any existing dashes and whitespace
        clean_data = ''.join(c for c in str(data) if c not in '- \t\n')

        # Split into groups and join with dashes
        groups = [clean_data[i:i + group_size] for i in range(0, len(clean_data), group_size)]
        return '-'.join(groups)

    @api.model
    def format_cu_invoice_number(self, sdc_id, receipt_number):
        """
        Format CU Invoice Number per TIS spec.

        Format: {CU_ID}/{Receipt_Number}

        Args:
            sdc_id: SDC/CU ID (e.g., "KRACU04XXXXXXXX")
            receipt_number: Receipt number from eTIMS

        Returns:
            Formatted CU Invoice Number (e.g., "KRACU04XXXXXXXX/12345")
        """
        if not sdc_id or not receipt_number:
            return ''
        return f"{sdc_id}/{receipt_number}"

    @api.model
    def format_receipt_counter(self, current_count, total_count, receipt_type='NS'):
        """
        Format receipt counter per TIS spec.

        Format: A/B RT where:
        - A = Counter (current count)
        - B = Total receipts
        - RT = Receipt type label

        Args:
            current_count: Current receipt counter
            total_count: Total receipts
            receipt_type: Receipt type code (NS, NC, CS, CC, TS, TC, PS)

        Returns:
            Formatted counter string (e.g., "123/500 NS")
        """
        return f"{current_count}/{total_count} {receipt_type}"

    @api.model
    def generate_qr_content(self, invoice_date, invoice_time, sdc_id, receipt_number,
                            internal_data, receipt_signature):
        """
        Generate QR code content per TIS spec Section 6.23.8.

        Format: date(ddmmyyyy)#time(hhmmss)#cu_number#receipt_number#internal_data#signature

        Args:
            invoice_date: Invoice date as datetime or string
            invoice_time: Invoice time as datetime or string (can be same as invoice_date if datetime)
            sdc_id: SDC/CU ID
            receipt_number: Receipt number
            internal_data: Internal data from eTIMS response
            receipt_signature: Receipt signature from eTIMS response

        Returns:
            QR code content string
        """
        # Format date as ddmmyyyy
        if hasattr(invoice_date, 'strftime'):
            date_str = invoice_date.strftime('%d%m%Y')
        else:
            # Assume YYYYMMDDHHmmss format, convert to ddmmyyyy
            date_str = str(invoice_date)
            if len(date_str) >= 8:
                date_str = date_str[6:8] + date_str[4:6] + date_str[0:4]

        # Format time as hhmmss
        if hasattr(invoice_time, 'strftime'):
            time_str = invoice_time.strftime('%H%M%S')
        else:
            # Assume YYYYMMDDHHmmss format, extract time
            time_str = str(invoice_time)
            if len(time_str) >= 14:
                time_str = time_str[8:14]
            elif len(time_str) >= 6:
                time_str = time_str[:6]
            else:
                time_str = '000000'

        # Build QR content
        parts = [
            date_str,
            time_str,
            str(sdc_id or ''),
            str(receipt_number or ''),
            str(internal_data or ''),
            str(receipt_signature or ''),
        ]

        return '#'.join(parts)

    @api.model
    def generate_qr_code_image(self, content, box_size=10, border=4):
        """
        Generate QR code image as base64 encoded PNG.

        Args:
            content: QR code content string
            box_size: Size of each box in pixels (default 10)
            border: Border size in boxes (default 4)

        Returns:
            Base64 encoded PNG image string, or False if qrcode library not available
        """
        if not HAS_QRCODE:
            _logger.warning('Cannot generate QR code: qrcode library not installed')
            return False

        if not content:
            return False

        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=box_size,
                border=border,
            )
            qr.add_data(content)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            return base64.b64encode(buffer.getvalue()).decode('utf-8')

        except Exception as e:
            _logger.error('Failed to generate QR code: %s', str(e))
            return False

    @api.model
    def get_receipt_type_label(self, transaction_type, receipt_type):
        """
        Get the two-letter receipt type label per TIS spec Section 4.

        Args:
            transaction_type: 'NORMAL', 'COPY', 'TRAINING', or 'PROFORMA'
            receipt_type: 'SALES' or 'CREDIT_NOTE'

        Returns:
            Receipt type label (NS, NC, CS, CC, TS, TC, or PS)
        """
        labels = {
            ('NORMAL', 'SALES'): 'NS',
            ('NORMAL', 'CREDIT_NOTE'): 'NC',
            ('COPY', 'SALES'): 'CS',
            ('COPY', 'CREDIT_NOTE'): 'CC',
            ('TRAINING', 'SALES'): 'TS',
            ('TRAINING', 'CREDIT_NOTE'): 'TC',
            ('PROFORMA', 'SALES'): 'PS',
        }
        return labels.get((transaction_type, receipt_type), 'NS')


class AccountMoveReceiptMixin(models.Model):
    """
    Extend account.move with receipt formatting capabilities.
    """
    _inherit = 'account.move'

    def get_formatted_internal_data(self):
        """Get internal data formatted with dashes per TIS spec."""
        self.ensure_one()
        mixin = self.env['etims.receipt.mixin']
        return mixin.format_with_dashes(self.etims_intrl_data)

    def get_formatted_receipt_signature(self):
        """Get receipt signature formatted with dashes per TIS spec."""
        self.ensure_one()
        mixin = self.env['etims.receipt.mixin']
        return mixin.format_with_dashes(self.etims_rcpt_sign)

    def get_etims_qr_content(self):
        """Generate QR code content for this invoice per TIS spec."""
        self.ensure_one()
        if not self.etims_submitted:
            return ''

        mixin = self.env['etims.receipt.mixin']
        return mixin.generate_qr_content(
            invoice_date=self.etims_sdc_datetime or self.invoice_date,
            invoice_time=self.etims_sdc_datetime or self.invoice_date,
            sdc_id=self.etims_sdc_id,
            receipt_number=self.etims_rcpt_no,
            internal_data=self.etims_intrl_data,
            receipt_signature=self.etims_rcpt_sign,
        )

    def get_etims_qr_image(self):
        """Generate QR code image as base64 for this invoice."""
        self.ensure_one()
        content = self.get_etims_qr_content()
        if not content:
            return False

        mixin = self.env['etims.receipt.mixin']
        return mixin.generate_qr_code_image(content)
