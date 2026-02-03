# -*- coding: utf-8 -*-
from odoo import api, fields, models


class GhanaPayeTaxBand(models.Model):
    _name = 'ghana.paye.tax.band'
    _description = 'Ghana PAYE Tax Band'
    _order = 'lower_limit'

    name = fields.Char(string='Name', required=True)
    lower_limit = fields.Float(string='Lower Limit (Monthly)', required=True)
    upper_limit = fields.Float(string='Upper Limit (Monthly)', required=True)
    rate = fields.Float(string='Tax Rate (%)', required=True)
    active = fields.Boolean(default=True)

    @api.model
    def calculate_paye(self, taxable_income):
        """Calculate PAYE tax based on tax bands."""
        bands = self.search([('active', '=', True)], order='lower_limit')
        tax = 0.0

        for band in bands:
            if taxable_income <= 0:
                break

            if taxable_income > band.lower_limit:
                taxable_in_band = min(taxable_income, band.upper_limit) - band.lower_limit
                if taxable_in_band > 0:
                    tax += taxable_in_band * (band.rate / 100)

        return round(tax, 2)
