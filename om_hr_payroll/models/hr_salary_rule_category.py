# -*- coding: utf-8 -*-
from odoo import models, fields


class HrSalaryRuleCategory(models.Model):
    _name = 'hr.salary.rule.category'
    _description = 'Salary Rule Category'

    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    parent_id = fields.Many2one(
        'hr.salary.rule.category',
        string='Parent',
        help="Linking a salary category to its parent allows to group similar items."
    )
    children_ids = fields.One2many(
        'hr.salary.rule.category',
        'parent_id',
        string='Children'
    )
    note = fields.Text(string='Description')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
