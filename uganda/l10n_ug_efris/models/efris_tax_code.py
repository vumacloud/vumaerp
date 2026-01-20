# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class EfrisTaxCode(models.Model):
    _name = 'efris.tax.code'
    _description = 'EFRIS Tax Code'
    _rec_name = 'name'
    _order = 'code'

    code = fields.Char(
        string='Tax Code',
        required=True,
        help='EFRIS tax category code',
    )
    name = fields.Char(
        string='Description',
        required=True,
    )
    rate = fields.Float(
        string='Tax Rate (%)',
        help='Standard tax rate for this category',
    )
    tax_type = fields.Selection([
        ('vat', 'VAT'),
        ('excise', 'Excise Duty'),
        ('stamp', 'Stamp Duty'),
        ('exempt', 'Exempt'),
        ('zero', 'Zero-Rated'),
    ], string='Tax Type', required=True, default='vat')

    active = fields.Boolean(default=True)

    # Link to Odoo tax
    tax_ids = fields.Many2many(
        'account.tax',
        'efris_tax_code_account_tax_rel',
        'efris_tax_code_id',
        'tax_id',
        string='Related Taxes',
        help='Odoo taxes mapped to this EFRIS code',
    )

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'EFRIS tax code must be unique!'),
    ]

    @api.model
    def get_tax_code(self, tax_id):
        """Get EFRIS tax code for an Odoo tax."""
        if not tax_id:
            return False

        code = self.search([
            ('tax_ids', 'in', [tax_id.id])
        ], limit=1)

        return code.code if code else '01'  # Default to standard VAT


class EfrisGoodsCode(models.Model):
    _name = 'efris.goods.code'
    _description = 'EFRIS Goods/Services Code'
    _rec_name = 'name'
    _order = 'code'

    code = fields.Char(
        string='Item Code',
        required=True,
        help='EFRIS goods/services classification code',
    )
    name = fields.Char(
        string='Description',
        required=True,
    )
    category = fields.Selection([
        ('goods', 'Goods'),
        ('services', 'Services'),
    ], string='Category', required=True, default='goods')

    unit_code = fields.Char(
        string='Unit Code',
        help='EFRIS unit of measure code',
    )

    parent_id = fields.Many2one(
        'efris.goods.code',
        string='Parent Category',
    )
    child_ids = fields.One2many(
        'efris.goods.code',
        'parent_id',
        string='Sub-categories',
    )

    active = fields.Boolean(default=True)

    # Link to Odoo products
    product_category_ids = fields.Many2many(
        'product.category',
        'efris_goods_code_product_cat_rel',
        'efris_goods_code_id',
        'product_category_id',
        string='Product Categories',
        help='Odoo product categories mapped to this code',
    )

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'EFRIS goods code must be unique!'),
    ]
