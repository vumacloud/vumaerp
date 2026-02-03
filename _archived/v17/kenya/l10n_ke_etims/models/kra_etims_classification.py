# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class KRAeTIMSClassification(models.Model):
    _name = 'kra.etims.classification'
    _description = 'KRA e-TIMS Item Classification'
    _order = 'code, item_code'

    code = fields.Char(
        string='Code Class',
        required=True,
        help='Code classification (e.g., 01 for Item Classification)'
    )
    
    item_code = fields.Char(
        string='Item Code',
        required=True,
        index=True
    )
    
    name = fields.Char(
        string='Name',
        required=True
    )
    
    description = fields.Text(
        string='Description'
    )
    
    level = fields.Integer(
        string='Level',
        help='Classification hierarchy level'
    )
    
    parent_code = fields.Char(
        string='Parent Code',
        help='Upper level classification code'
    )
    
    use_yn = fields.Boolean(
        string='Active',
        default=True
    )
    
    _sql_constraints = [
        ('unique_classification', 'UNIQUE(code, item_code)', 
         'Classification code must be unique!')
    ]
    
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.item_code}] {record.name}"
            result.append((record.id, name))
        return result
    
    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            domain = ['|', ('item_code', operator, name), ('name', operator, name)]
        return self._search(domain, limit=limit, order=order)
