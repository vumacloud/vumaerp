# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class EfrisDocumentType(models.Model):
    _name = 'efris.document.type'
    _description = 'EFRIS Document Type'
    _rec_name = 'name'
    _order = 'code'

    code = fields.Char(
        string='Document Code',
        required=True,
        help='EFRIS document type code',
    )
    name = fields.Char(
        string='Document Type',
        required=True,
    )
    description = fields.Text(string='Description')

    move_type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
        ('in_invoice', 'Vendor Bill'),
        ('in_refund', 'Vendor Credit Note'),
    ], string='Invoice Type', help='Corresponding Odoo invoice type')

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'EFRIS document type code must be unique!'),
    ]

    @api.model
    def get_document_type_code(self, move_type):
        """Get EFRIS document type code for Odoo invoice type."""
        doc_type = self.search([
            ('move_type', '=', move_type)
        ], limit=1)

        if doc_type:
            return doc_type.code

        # Default mapping
        mapping = {
            'out_invoice': '101',
            'out_refund': '102',
        }
        return mapping.get(move_type, '101')
