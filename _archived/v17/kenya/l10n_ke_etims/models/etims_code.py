# -*- coding: utf-8 -*-
from odoo import api, fields, models


class EtimsCode(models.Model):
    _name = 'etims.code'
    _description = 'eTIMS Code Table'
    _rec_name = 'name'

    code_type = fields.Selection([
        ('01', 'Item Classification'),
        ('02', 'Taxation Type'),
        ('03', 'Country'),
        ('04', 'Packaging Unit'),
        ('05', 'Quantity Unit'),
        ('06', 'Payment Type'),
        ('07', 'Transaction Type'),
        ('08', 'Stock Movement Type'),
        ('09', 'Product Type'),
        ('10', 'Import Status'),
    ], string='Code Type', required=True, index=True)

    code = fields.Char(string='Code', required=True, index=True)
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_type_uniq', 'unique(code_type, code)',
         'Code must be unique within its type.'),
    ]

    @api.model
    def create_or_update(self, vals):
        """Create or update a code record."""
        existing = self.search([
            ('code_type', '=', vals.get('code_type')),
            ('code', '=', vals.get('code')),
        ], limit=1)

        if existing:
            existing.write(vals)
            return existing
        return self.create(vals)

    @api.model
    def get_code(self, code_type, code):
        """Get a specific code record."""
        return self.search([
            ('code_type', '=', code_type),
            ('code', '=', code),
        ], limit=1)

    @api.model
    def get_codes_by_type(self, code_type):
        """Get all codes of a specific type."""
        return self.search([('code_type', '=', code_type)])


class EtimsItemClass(models.Model):
    _name = 'etims.item.class'
    _description = 'eTIMS Item Classification'
    _rec_name = 'name'

    code = fields.Char(string='Classification Code', required=True, index=True)
    name = fields.Char(string='Name', required=True)
    tax_type = fields.Char(string='Tax Type Code')
    tax_rate = fields.Float(string='Tax Rate (%)')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Classification code must be unique.'),
    ]
