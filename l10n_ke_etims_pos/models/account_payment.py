# -*- coding: utf-8 -*-
"""
Account Payment eTIMS Integration

Per KRA eTIMS regulations, sales should be submitted when payment is received,
not just when an invoice is posted. This ensures fiscal compliance by reporting
actual sales transactions at the point of payment.

This module triggers eTIMS submission when:
1. A payment is registered and reconciled against a customer invoice
2. The invoice becomes fully paid

For partial payments, the submission occurs when the invoice reaches full payment.
"""
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        """
        Override payment posting to trigger eTIMS submission when payment is received.

        eTIMS submission is triggered when:
        - Payment is for a customer invoice (not vendor bill)
        - The invoice is posted and not yet submitted to eTIMS
        - The company is Kenyan (country_code = 'KE')
        """
        res = super().action_post()

        # Process eTIMS submission for each payment
        for payment in self:
            payment._check_etims_submission()

        return res

    def _check_etims_submission(self):
        """
        Check if this payment should trigger eTIMS submission for related invoices.

        We submit to eTIMS when:
        1. Payment is a customer receipt (inbound payment)
        2. The reconciled invoices are fully paid
        3. The invoice hasn't been submitted to eTIMS yet
        """
        self.ensure_one()

        # Only process customer payments (inbound)
        if self.payment_type != 'inbound':
            return

        # Check if company is Kenyan
        if self.company_id.country_id.code != 'KE':
            return

        # Check if eTIMS is configured
        try:
            config = self.env['etims.config'].get_config(self.company_id)
        except UserError:
            # eTIMS not configured, skip
            return

        # Get invoices being paid
        # In Odoo 17, we need to check the reconciled move lines
        invoices_to_submit = self._get_paid_invoices_for_etims()

        for invoice in invoices_to_submit:
            try:
                invoice._auto_submit_etims_on_payment()
            except Exception as e:
                _logger.warning(
                    'Failed to auto-submit invoice %s to eTIMS after payment: %s',
                    invoice.name, str(e)
                )
                # Don't block payment - log warning but continue

    def _get_paid_invoices_for_etims(self):
        """
        Get invoices that should be submitted to eTIMS based on this payment.

        Returns invoices that:
        - Are customer invoices (out_invoice) or credit notes (out_refund)
        - Are fully paid (payment_state in ['paid', 'in_payment'])
        - Have not been submitted to eTIMS yet
        """
        self.ensure_one()

        invoices = self.env['account.move']

        # Get reconciled invoices from the payment
        if self.reconciled_invoice_ids:
            invoices = self.reconciled_invoice_ids.filtered(
                lambda inv: (
                    inv.move_type in ('out_invoice', 'out_refund') and
                    inv.state == 'posted' and
                    not inv.etims_submitted and
                    inv.payment_state in ('paid', 'in_payment')
                )
            )

        return invoices


class AccountPaymentRegister(models.TransientModel):
    """
    Handles batch payment registration wizard.
    Ensures eTIMS submission is triggered for invoices paid through this wizard.
    """
    _inherit = 'account.payment.register'

    def _create_payments(self):
        """
        Override to ensure eTIMS submission happens after batch payments.
        """
        payments = super()._create_payments()

        # The payment.action_post() already handles eTIMS submission
        # but we ensure it's called for any edge cases
        for payment in payments:
            if payment.state == 'posted':
                payment._check_etims_submission()

        return payments
