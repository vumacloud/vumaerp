# Part of VumaERP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

# GRA E-VAT Tax Code Mappings
# Reference: GRA E-VAT API Documentation
#
# TAX CODES:
# TAX_A: 0% - Exempted supplies
# TAX_B: 15% - Standard taxable supplies (VAT)
# TAX_C: 0% - Export (zero-rated)
# TAX_D: 0% - Non-taxable supplies
# TAX_E: 3% - Non-VAT (flat rate for retailers)
#
# LEVY CODES (VAT Act 1151, effective January 2026):
# LEVY_A: 2.5% - NHIL (National Health Insurance Levy) - Now input deductible
# LEVY_B: 2.5% - GETFund (Ghana Education Trust Fund) - Now input deductible
# LEVY_C: ABOLISHED - Was COVID-19 Health Recovery Levy (1%)
# LEVY_D: 1%/5% - Tourism Levy / Communication Service Tax


class GhanaEvatTaxCode(models.Model):
    _name = 'ghana.evat.tax.code'
    _description = 'Ghana E-VAT Tax Code'
    _order = 'sequence, code'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True, help='GRA tax/levy code (e.g., TAX_B, LEVY_A)')
    rate = fields.Float(string='Rate (%)', digits=(5, 2), help='Tax rate as percentage')
    code_type = fields.Selection([
        ('tax', 'Tax'),
        ('levy', 'Levy'),
    ], string='Type', required=True, default='tax')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', default=10)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Tax code must be unique.'),
    ]

    @api.model
    def get_tax_code(self, code):
        """
        Get tax code record by code.

        Args:
            code: GRA tax code (e.g., 'TAX_B')

        Returns:
            ghana.evat.tax.code record or False
        """
        return self.search([('code', '=', code), ('active', '=', True)], limit=1)

    @api.model
    def get_tax_rate(self, code):
        """
        Get tax rate for a code.

        Args:
            code: GRA tax code (e.g., 'TAX_B')

        Returns:
            float: Tax rate as decimal (e.g., 0.15 for 15%)
        """
        tax_code = self.get_tax_code(code)
        return tax_code.rate / 100 if tax_code else 0.0

    @api.model
    def get_combined_rate(self, tax_codes):
        """
        Calculate combined rate for multiple tax codes.

        Args:
            tax_codes: List of GRA tax codes

        Returns:
            float: Combined tax rate as decimal
        """
        total = 0.0
        for code in tax_codes:
            total += self.get_tax_rate(code)
        return total

    @api.model
    def map_odoo_tax_to_gra(self, tax):
        """
        Map Odoo tax to GRA tax code.

        This method attempts to map an Odoo account.tax record to the
        appropriate GRA tax code based on the tax amount and type.

        Args:
            tax: account.tax record

        Returns:
            str: GRA tax code (TAX_A through TAX_E)
        """
        if not tax:
            return 'TAX_D'  # Non-taxable

        amount = tax.amount

        # Check tax name/description for hints
        name_lower = (tax.name or '').lower()

        # Zero-rated exports
        if 'export' in name_lower:
            return 'TAX_C'

        # Exempted
        if 'exempt' in name_lower or amount == 0:
            return 'TAX_A'

        # Standard VAT (15%)
        if 14.5 <= amount <= 15.5:
            return 'TAX_B'

        # Non-VAT flat rate (3%)
        if 2.5 <= amount <= 3.5:
            return 'TAX_E'

        # Default to standard taxable if positive rate
        if amount > 0:
            return 'TAX_B'

        return 'TAX_D'  # Non-taxable

    @api.model
    def get_applicable_levies(self, tax_code):
        """
        Get applicable levies for a tax code.

        Under VAT Act 1151 (January 2026), NHIL and GETFund apply to
        standard taxable supplies (TAX_B).

        Args:
            tax_code: GRA tax code

        Returns:
            list: List of applicable levy codes
        """
        # NHIL and GETFund apply to standard taxable supplies
        if tax_code == 'TAX_B':
            return ['LEVY_A', 'LEVY_B']  # NHIL, GETFund
        return []
