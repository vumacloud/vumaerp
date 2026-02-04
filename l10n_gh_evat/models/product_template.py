# -*- coding: utf-8 -*-
from odoo import api, models, _
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to automatically assign Ghana taxes (VAT 15%, NHIL 2.5%, GETFund 2.5%)
        to new products when the company uses Ghana fiscal localization.
        """
        products = super().create(vals_list)

        # Auto-assign Ghana taxes to products that don't have taxes set
        for product in products:
            if self._should_apply_ghana_taxes(product):
                self._apply_ghana_taxes(product)

        return products

    def _should_apply_ghana_taxes(self, product):
        """
        Check if Ghana taxes should be auto-applied to this product.
        Returns True if:
        - Company's fiscal country is Ghana
        - Product doesn't already have customer taxes set
        - Product is saleable
        """
        company = product.company_id or self.env.company

        # Check if company uses Ghana localization
        if company.account_fiscal_country_id.code != 'GH':
            return False

        # Don't override if taxes already explicitly set
        if product.taxes_id:
            return False

        # Only apply to saleable products
        if not product.sale_ok:
            return False

        return True

    def _apply_ghana_taxes(self, product):
        """
        Apply Ghana standard taxes (VAT 15%, NHIL 2.5%, GETFund 2.5%) to a product.
        """
        company = product.company_id or self.env.company

        # Find Ghana taxes by name pattern
        ghana_sale_taxes = self.env['account.tax'].search([
            ('company_id', '=', company.id),
            ('type_tax_use', '=', 'sale'),
            '|', '|',
            ('name', 'ilike', 'VAT 15%'),
            ('name', 'ilike', 'NHIL'),
            ('name', 'ilike', 'GETFund'),
        ])

        # Also try by tax group for more reliable matching
        if len(ghana_sale_taxes) < 3:
            ghana_sale_taxes = self.env['account.tax'].search([
                ('company_id', '=', company.id),
                ('type_tax_use', '=', 'sale'),
                ('amount', 'in', [15.0, 2.5]),  # VAT 15%, NHIL 2.5%, GETFund 2.5%
            ])

        if ghana_sale_taxes:
            product.taxes_id = [(6, 0, ghana_sale_taxes.ids)]
            _logger.info(
                'Auto-applied Ghana taxes to product "%s": %s',
                product.name,
                ', '.join(ghana_sale_taxes.mapped('name'))
            )

        # Apply purchase taxes too
        ghana_purchase_taxes = self.env['account.tax'].search([
            ('company_id', '=', company.id),
            ('type_tax_use', '=', 'purchase'),
            '|', '|',
            ('name', 'ilike', 'VAT 15%'),
            ('name', 'ilike', 'NHIL'),
            ('name', 'ilike', 'GETFund'),
        ])

        if ghana_purchase_taxes and not product.supplier_taxes_id:
            product.supplier_taxes_id = [(6, 0, ghana_purchase_taxes.ids)]
