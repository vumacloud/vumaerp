# -*- coding: utf-8 -*-
"""
POS Session eTIMS Integration

Handles batch submission of POS orders to eTIMS at session close.
This ensures any orders that failed to submit during real-time processing
are submitted before the session is closed.

Also provides session-level reporting and status tracking.
"""
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = 'pos.session'

    # eTIMS Session Stats
    etims_orders_submitted = fields.Integer(
        string='eTIMS Submitted Orders',
        compute='_compute_etims_stats',
        help='Number of orders submitted to eTIMS in this session'
    )
    etims_orders_pending = fields.Integer(
        string='eTIMS Pending Orders',
        compute='_compute_etims_stats',
        help='Number of orders pending eTIMS submission'
    )
    etims_orders_failed = fields.Integer(
        string='eTIMS Failed Orders',
        compute='_compute_etims_stats',
        help='Number of orders with eTIMS submission errors'
    )
    etims_submission_complete = fields.Boolean(
        string='eTIMS Submission Complete',
        compute='_compute_etims_stats',
        help='True if all orders have been submitted to eTIMS'
    )

    @api.depends('order_ids.etims_submitted', 'order_ids.etims_submission_error')
    def _compute_etims_stats(self):
        for session in self:
            orders = session.order_ids.filtered(
                lambda o: o.state in ('paid', 'done', 'invoiced')
            )
            session.etims_orders_submitted = len(orders.filtered('etims_submitted'))
            session.etims_orders_failed = len(orders.filtered(
                lambda o: not o.etims_submitted and o.etims_submission_error
            ))
            session.etims_orders_pending = len(orders.filtered(
                lambda o: not o.etims_submitted and not o.etims_submission_error
            ))
            session.etims_submission_complete = (
                session.etims_orders_pending == 0 and
                session.etims_orders_failed == 0
            )

    def _validate_session(self):
        """
        Override to check eTIMS submission status before closing session.
        Allows closing with warnings if submissions failed.
        """
        res = super()._validate_session()

        # Check eTIMS submission status for Kenyan companies
        for session in self:
            if session.company_id.country_id.code != 'KE':
                continue

            # Try to submit any pending orders before final close
            session._submit_pending_etims_orders()

            # Warn if there are failed submissions
            if session.etims_orders_failed > 0:
                _logger.warning(
                    'POS Session %s closed with %d failed eTIMS submissions',
                    session.name, session.etims_orders_failed
                )

        return res

    def action_pos_session_close(self):
        """
        Override session close to submit pending eTIMS orders.
        """
        # First, try to submit any pending orders
        for session in self:
            if session.company_id.country_id.code == 'KE':
                session._submit_pending_etims_orders()

        return super().action_pos_session_close()

    def _submit_pending_etims_orders(self):
        """
        Submit all pending POS orders to eTIMS.
        Called at session close to ensure all orders are submitted.
        """
        self.ensure_one()

        # Find orders that need submission
        pending_orders = self.order_ids.filtered(
            lambda o: (
                o.state in ('paid', 'done', 'invoiced') and
                not o.etims_submitted
            )
        )

        if not pending_orders:
            return

        success_count = 0
        fail_count = 0

        for order in pending_orders:
            try:
                if order._validate_etims_submission():
                    if order._submit_to_etims():
                        success_count += 1
                    else:
                        fail_count += 1
            except Exception as e:
                _logger.warning(
                    'Failed to submit POS order %s to eTIMS: %s',
                    order.name, str(e)
                )
                order.etims_submission_error = str(e)
                fail_count += 1

        _logger.info(
            'POS Session %s: Submitted %d orders to eTIMS, %d failed',
            self.name, success_count, fail_count
        )

    def action_submit_pending_etims(self):
        """Manual action to retry submitting pending eTIMS orders."""
        self.ensure_one()

        self._submit_pending_etims_orders()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('eTIMS Submission'),
                'message': _(
                    'Submitted: %d, Pending: %d, Failed: %d'
                ) % (
                    self.etims_orders_submitted,
                    self.etims_orders_pending,
                    self.etims_orders_failed
                ),
                'type': 'success' if self.etims_submission_complete else 'warning',
            }
        }

    def action_view_etims_pending(self):
        """View orders pending eTIMS submission."""
        self.ensure_one()
        pending_orders = self.order_ids.filtered(
            lambda o: not o.etims_submitted and o.state in ('paid', 'done', 'invoiced')
        )
        return {
            'name': _('Pending eTIMS Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', pending_orders.ids)],
            'context': {'create': False},
        }

    def action_view_etims_failed(self):
        """View orders with failed eTIMS submission."""
        self.ensure_one()
        failed_orders = self.order_ids.filtered(
            lambda o: not o.etims_submitted and o.etims_submission_error
        )
        return {
            'name': _('Failed eTIMS Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', failed_orders.ids)],
            'context': {'create': False},
        }


class PosConfig(models.Model):
    """
    Extend POS Config for eTIMS settings.
    """
    _inherit = 'pos.config'

    etims_auto_submit = fields.Boolean(
        string='Auto-submit to eTIMS',
        default=True,
        help='Automatically submit POS orders to eTIMS when payment is completed'
    )
    etims_block_on_failure = fields.Boolean(
        string='Block on eTIMS Failure',
        default=False,
        help='If enabled, POS operations will be blocked if eTIMS submission fails. '
             'Disable this for offline capability.'
    )

    def get_limited_partners_loading(self):
        """Override to include eTIMS settings in POS."""
        result = super().get_limited_partners_loading()
        return result
