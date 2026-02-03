# -*- coding: utf-8 -*-
from odoo import api, fields, models


class NigeriaTaxCode(models.Model):
    _name = 'nigeria.tax.code'
    _description = 'Nigeria Tax Code'
    _rec_name = 'name'
    _order = 'code'

    code = fields.Char(string='Tax Code', required=True)
    name = fields.Char(string='Tax Name', required=True)
    description = fields.Text(string='Description')
    rate = fields.Float(string='Rate (%)', default=0.0)
    tax_type = fields.Selection([
        ('vat', 'VAT'),
        ('wht', 'Withholding Tax'),
        ('cit', 'Company Income Tax'),
        ('ppt', 'Petroleum Profits Tax'),
        ('edt', 'Education Tax'),
        ('stamp', 'Stamp Duty'),
        ('cgt', 'Capital Gains Tax'),
        ('exempt', 'Exempt'),
        ('zero', 'Zero Rated'),
    ], string='Tax Type', required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Tax code must be unique!'),
    ]
