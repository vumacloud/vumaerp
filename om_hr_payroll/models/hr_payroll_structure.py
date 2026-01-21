# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrPayrollStructure(models.Model):
    _name = 'hr.payroll.structure'
    _description = 'Salary Structure'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Reference', required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    note = fields.Text(string='Description')
    parent_id = fields.Many2one(
        'hr.payroll.structure',
        string='Parent'
    )
    children_ids = fields.One2many(
        'hr.payroll.structure',
        'parent_id',
        string='Children'
    )
    rule_ids = fields.Many2many(
        'hr.salary.rule',
        'hr_structure_salary_rule_rel',
        'struct_id',
        'rule_id',
        string='Salary Rules'
    )
    active = fields.Boolean(default=True)

    @api.model
    def _get_parent_structure(self):
        """Get parent structures"""
        parent = self.mapped('parent_id')
        if parent:
            parent = parent._get_parent_structure()
        return parent + self

    def get_all_rules(self):
        """Get all rules from this structure and parents"""
        all_rules = self.env['hr.salary.rule']
        for struct in self._get_parent_structure():
            all_rules |= struct.rule_ids
        return all_rules
