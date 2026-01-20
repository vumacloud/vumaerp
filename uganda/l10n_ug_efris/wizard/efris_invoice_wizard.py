# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EfrisInvoiceWizard(models.TransientModel):
    _name = 'efris.invoice.wizard'
    _description = 'EFRIS Invoice Submission Wizard'

    move_ids = fields.Many2many(
        'account.move',
        string='Invoices',
        domain=[
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('efris_submitted', '=', False),
        ],
    )
    buyer_type = fields.Selection([
        ('0', 'Business (B2B)'),
        ('1', 'Individual (B2C)'),
        ('2', 'Government'),
        ('3', 'Foreigner'),
    ], string='Buyer Type', default='0')

    include_all_pending = fields.Boolean(
        string='Include All Pending',
        default=False,
        help='Include all invoices pending EFRIS submission',
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        active_ids = self._context.get('active_ids', [])
        if active_ids:
            moves = self.env['account.move'].browse(active_ids).filtered(
                lambda m: m.move_type in ['out_invoice', 'out_refund']
                and m.state == 'posted'
                and not m.efris_submitted
            )
            res['move_ids'] = [(6, 0, moves.ids)]

        return res

    @api.onchange('include_all_pending')
    def _onchange_include_all_pending(self):
        if self.include_all_pending:
            pending_moves = self.env['account.move'].search([
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted'),
                ('efris_submitted', '=', False),
                ('company_id', '=', self.env.company.id),
            ])
            self.move_ids = pending_moves

    def action_submit(self):
        """Submit selected invoices to EFRIS."""
        self.ensure_one()

        if not self.move_ids:
            raise UserError(_("Please select at least one invoice to submit."))

        # Update buyer type on all invoices
        if self.buyer_type:
            self.move_ids.write({'efris_buyer_type': self.buyer_type})

        submitted = 0
        errors = []

        for move in self.move_ids:
            try:
                move.action_submit_to_efris()
                submitted += 1
            except UserError as e:
                errors.append(f"{move.name}: {str(e)}")

        message = _("%d invoice(s) submitted successfully.") % submitted
        if errors:
            message += _("\n\nErrors:\n") + "\n".join(errors)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('EFRIS Submission Complete'),
                'message': message,
                'type': 'success' if not errors else 'warning',
                'sticky': True if errors else False,
            }
        }


class EfrisGoodsRegistrationWizard(models.TransientModel):
    _name = 'efris.goods.registration.wizard'
    _description = 'EFRIS Goods Registration Wizard'

    product_ids = fields.Many2many(
        'product.template',
        string='Products',
        domain=[('efris_registered', '=', False)],
    )
    goods_code_id = fields.Many2one(
        'efris.goods.code',
        string='EFRIS Goods Category',
        required=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        active_ids = self._context.get('active_ids', [])
        if active_ids and self._context.get('active_model') == 'product.template':
            products = self.env['product.template'].browse(active_ids).filtered(
                lambda p: not p.efris_registered
            )
            res['product_ids'] = [(6, 0, products.ids)]

        return res

    def action_register(self):
        """Register products with EFRIS."""
        self.ensure_one()

        if not self.product_ids:
            raise UserError(_("Please select at least one product to register."))

        # Update EFRIS goods code on products
        self.product_ids.write({
            'efris_goods_code': self.goods_code_id.code,
        })

        # TODO: Actually submit to EFRIS API for goods registration
        # For now, just mark as registered with the goods code
        registered = len(self.product_ids)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Products Updated'),
                'message': _("%d product(s) assigned EFRIS goods code: %s") % (
                    registered, self.goods_code_id.code
                ),
                'type': 'success',
                'sticky': False,
            }
        }
