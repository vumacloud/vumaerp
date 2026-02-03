# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Nigeria tax fields
    ng_wht_applicable = fields.Boolean(
        string='WHT Applicable',
        default=False,
        help='Withholding Tax applies to this transaction',
    )
    ng_wht_rate = fields.Float(
        string='WHT Rate (%)',
        default=5.0,
    )
    ng_wht_amount = fields.Monetary(
        string='WHT Amount',
        compute='_compute_ng_wht',
        currency_field='currency_id',
    )
    ng_vat_amount = fields.Monetary(
        string='VAT Amount',
        compute='_compute_ng_vat',
        currency_field='currency_id',
    )

    @api.depends('amount_untaxed', 'ng_wht_applicable', 'ng_wht_rate')
    def _compute_ng_wht(self):
        for move in self:
            if move.ng_wht_applicable and move.ng_wht_rate:
                move.ng_wht_amount = move.amount_untaxed * (move.ng_wht_rate / 100)
            else:
                move.ng_wht_amount = 0

    @api.depends('amount_tax')
    def _compute_ng_vat(self):
        for move in self:
            # Simplified - assumes all tax is VAT
            move.ng_vat_amount = move.amount_tax
