# -*- coding: utf-8 -*-
from odoo import api, fields, models


class GhanaEvatTaxCode(models.Model):
    _name = 'ghana.evat.tax.code'
    _description = 'Ghana E-VAT Tax Code'
    _order = 'sequence, code'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    rate = fields.Float(string='Rate (%)', digits=(5, 2))
    code_type = fields.Selection([
        ('tax', 'Tax'),
        ('levy', 'Levy'),
    ], string='Type', required=True, default='tax')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Tax code must be unique.'),
    ]

    @api.model
    def get_tax_code(self, code):
        """Get tax code record by code."""
        return self.search([('code', '=', code), ('active', '=', True)], limit=1)

    @api.model
    def get_tax_rate(self, code):
        """Get tax rate for a code as decimal."""
        tax_code = self.get_tax_code(code)
        return tax_code.rate / 100 if tax_code else 0.0

    @api.model
    def map_odoo_tax_to_gra(self, tax):
        """Map Odoo tax to GRA tax code."""
        if not tax:
            return 'TAX_D'

        amount = tax.amount
        name_lower = (tax.name or '').lower()

        if 'export' in name_lower:
            return 'TAX_C'
        if 'exempt' in name_lower or amount == 0:
            return 'TAX_A'
        if 14.5 <= amount <= 15.5:
            return 'TAX_B'
        if 2.5 <= amount <= 3.5:
            return 'TAX_E'
        if amount > 0:
            return 'TAX_B'

        return 'TAX_D'
