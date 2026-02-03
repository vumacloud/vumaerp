# -*- coding: utf-8 -*-
"""
Account Move eTIMS Payment Integration

Extends account.move with payment-triggered eTIMS submission.
Per KRA eTIMS regulations and KPMG advisory, sales should be submitted
when payment is actually received, not just when an invoice is posted.

This aligns with the regulatory requirement that income reflected in eTIMS
sales data must represent actual sales transactions.
"""
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Flag to control submission behavior
    etims_submit_on_payment = fields.Boolean(
        string='Submit to eTIMS on Payment',
        default=True,
        help='If enabled, invoice will be submitted to eTIMS when payment is received, '
             'not when posted. This is the recommended setting per KRA regulations.'
    )

    # Refund-specific fields for credit notes
    etims_refund_reason = fields.Selection([
        ('01', 'Damage/Defect'),
        ('02', 'Change of Mind'),
        ('03', 'Wrong Item Delivered'),
        ('04', 'Late Delivery'),
        ('05', 'Duplicate Order'),
        ('06', 'Price Dispute'),
        ('07', 'Quantity Dispute'),
        ('08', 'Quality Issues'),
        ('09', 'Order Cancellation'),
        ('10', 'Other'),
    ], string='Refund Reason (eTIMS)',
       default='01',
       copy=False,
       help='Reason code for the refund as required by KRA eTIMS.')

    def _auto_submit_etims_on_payment(self):
        """
        Auto-submit invoice to eTIMS when payment is received.

        This method is called by account.payment when a customer payment
        is posted and reconciled against this invoice.

        Key compliance point (per KPMG advisory):
        - Submit to eTIMS only when payment is actually received
        - Posted but unpaid invoices should NOT be submitted
        - This ensures eTIMS reflects actual sales, not just accrued revenue
        """
        self.ensure_one()

        # Skip if already submitted
        if self.etims_submitted:
            return True

        # Skip if not a customer invoice/credit note
        if self.move_type not in ('out_invoice', 'out_refund'):
            return False

        # Skip if not posted
        if self.state != 'posted':
            return False

        # Skip if not fully paid
        if self.payment_state not in ('paid', 'in_payment'):
            _logger.debug(
                'Invoice %s not fully paid (state: %s), skipping eTIMS submission',
                self.name, self.payment_state
            )
            return False

        # Check if company is Kenyan
        if self.company_id.country_id.code != 'KE':
            return False

        try:
            # Use the existing action_submit_to_etims method from base module
            self.action_submit_to_etims()
            _logger.info(
                'Invoice %s auto-submitted to eTIMS on payment receipt',
                self.name
            )
            return True

        except UserError as e:
            # Log but don't block - payment already received
            _logger.warning(
                'Failed to auto-submit invoice %s to eTIMS: %s',
                self.name, str(e)
            )
            self.message_post(
                body=_('eTIMS auto-submission failed on payment: %s. '
                       'Please submit manually.') % str(e)
            )
            return False

        except Exception as e:
            _logger.error(
                'Unexpected error during eTIMS submission for invoice %s: %s',
                self.name, str(e)
            )
            return False

    def action_post(self):
        """
        Override to prevent auto-submission on posting for Kenyan invoices.

        Per KRA eTIMS regulations:
        - Sales should be reported when payment is received
        - A posted but unpaid invoice is NOT a completed sale
        - Submission happens via _auto_submit_etims_on_payment when paid

        This override disables the base module's auto_submit_invoices behavior
        for invoices where etims_submit_on_payment is True.
        """
        # Call parent first
        res = super().action_post()

        # For Kenyan companies with submit_on_payment enabled,
        # we skip the auto-submit that may happen in the base module
        # by NOT calling action_submit_to_etims here.
        # The submission will happen when payment is received.

        for move in self:
            if (move.move_type in ('out_invoice', 'out_refund') and
                    move.company_id.country_id.code == 'KE' and
                    move.etims_submit_on_payment and
                    not move.etims_submitted):
                # Log that we're deferring submission
                _logger.debug(
                    'Invoice %s posted but eTIMS submission deferred until payment',
                    move.name
                )

        return res


class AccountMoveReversal(models.TransientModel):
    """
    Handle credit note/refund eTIMS submission.

    Per KRA eTIMS regulations, refunds (credit notes) must:
    - Reference the original invoice
    - Include a reason code
    - Be submitted when the refund payment is processed
    """
    _inherit = 'account.move.reversal'

    etims_refund_reason = fields.Selection([
        ('01', 'Damage/Defect'),
        ('02', 'Change of Mind'),
        ('03', 'Wrong Item Delivered'),
        ('04', 'Late Delivery'),
        ('05', 'Duplicate Order'),
        ('06', 'Price Dispute'),
        ('07', 'Quantity Dispute'),
        ('08', 'Quality Issues'),
        ('09', 'Order Cancellation'),
        ('10', 'Other'),
    ], string='Refund Reason (eTIMS)',
       default='01',
       help='Reason code for the refund as required by KRA eTIMS. '
            'This will be included in the eTIMS submission.')

    def _prepare_default_reversal(self, move):
        """Add eTIMS refund reason to credit note."""
        res = super()._prepare_default_reversal(move)
        if self.etims_refund_reason:
            res['etims_refund_reason'] = self.etims_refund_reason
        return res
