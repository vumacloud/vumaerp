# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    efris_goods_code = fields.Char(
        string='EFRIS Goods Code',
        help='EFRIS goods/services classification code for this product',
    )
    efris_registered = fields.Boolean(
        string='Registered with EFRIS',
        default=False,
        help='Whether this product has been registered with EFRIS',
    )
    efris_item_code = fields.Char(
        string='EFRIS Item Code',
        readonly=True,
        help='Item code assigned by EFRIS after registration',
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    efris_goods_code = fields.Char(
        related='product_tmpl_id.efris_goods_code',
        store=True,
        readonly=False,
    )
