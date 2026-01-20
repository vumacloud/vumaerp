# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EVATInvoiceWizard(models.TransientModel):
    _name = 'evat.invoice.wizard'
    _description = 'E-VAT Invoice Submission Wizard'

    move_ids = fields.Many2many(
        'account.move',
        string='Invoices',
        domain=[
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('evat_submitted', '=', False),
        ],
    )
    include_all_pending = fields.Boolean(
        string='Include All Pending',
        default=False,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        active_ids = self._context.get('active_ids', [])
        if active_ids:
            moves = self.env['account.move'].browse(active_ids).filtered(
                lambda m: m.move_type in ['out_invoice', 'out_refund']
                and m.state == 'posted'
                and not m.evat_submitted
            )
            res['move_ids'] = [(6, 0, moves.ids)]

        return res

    @api.onchange('include_all_pending')
    def _onchange_include_all_pending(self):
        if self.include_all_pending:
            pending_moves = self.env['account.move'].search([
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted'),
                ('evat_submitted', '=', False),
                ('company_id', '=', self.env.company.id),
            ])
            self.move_ids = pending_moves

    def action_submit(self):
        """Submit selected invoices to E-VAT."""
        self.ensure_one()

        if not self.move_ids:
            raise UserError(_("Please select at least one invoice to submit."))

        submitted = 0
        errors = []

        for move in self.move_ids:
            try:
                move.action_submit_to_evat()
                submitted += 1
            except UserError as e:
                errors.append(f"{move.name}: {str(e)}")

        message = _("%d invoice(s) submitted successfully to E-VAT.") % submitted
        if errors:
            message += _("\n\nErrors:\n") + "\n".join(errors)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('E-VAT Submission Complete'),
                'message': message,
                'type': 'success' if not errors else 'warning',
                'sticky': True if errors else False,
            }
        }
