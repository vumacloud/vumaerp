# -*- coding: utf-8 -*-
from odoo import api, fields, models


class GhanaEVATTaxCode(models.Model):
    _name = 'ghana.evat.tax.code'
    _description = 'Ghana E-VAT Tax Code'
    _rec_name = 'name'
    _order = 'code'

    code = fields.Char(string='Tax Code', required=True)
    name = fields.Char(string='Tax Name', required=True)
    description = fields.Text(string='Description')
    rate = fields.Float(string='Rate (%)', default=0.0)
    tax_type = fields.Selection([
        ('vat', 'VAT'),
        ('nhil', 'NHIL'),
        ('getfund', 'GETFund Levy'),
        ('covid', 'COVID-19 Levy'),
        ('csl', 'Communication Service Levy'),
        ('exempt', 'Exempt'),
        ('zero', 'Zero Rated'),
    ], string='Tax Type', required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Tax code must be unique!'),
    ]

    @api.model
    def get_combined_rate(self, tax_types=None):
        """Get combined tax rate for specified tax types."""
        if tax_types is None:
            tax_types = ['vat', 'nhil', 'getfund', 'covid']

        taxes = self.search([
            ('active', '=', True),
            ('tax_type', 'in', tax_types),
        ])

        return sum(tax.rate for tax in taxes)
