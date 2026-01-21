# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class HrSalaryRule(models.Model):
    _name = 'hr.salary.rule'
    _description = 'Salary Rule'
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    sequence = fields.Integer(string='Sequence', required=True, default=5)
    quantity = fields.Char(string='Quantity', default='1.0')
    category_id = fields.Many2one(
        'hr.salary.rule.category',
        string='Category',
        required=True
    )
    active = fields.Boolean(default=True)
    appears_on_payslip = fields.Boolean(
        string='Appears on Payslip',
        default=True
    )
    condition_select = fields.Selection([
        ('none', 'Always True'),
        ('range', 'Range'),
        ('python', 'Python Expression'),
    ], string='Condition Based on', default='none', required=True)
    condition_range = fields.Char(string='Range Based on')
    condition_range_min = fields.Float(string='Minimum Range')
    condition_range_max = fields.Float(string='Maximum Range')
    condition_python = fields.Text(
        string='Python Condition',
        default='result = True'
    )
    amount_select = fields.Selection([
        ('percentage', 'Percentage (%)'),
        ('fix', 'Fixed Amount'),
        ('code', 'Python Code'),
    ], string='Amount Type', required=True, default='fix')
    amount_fix = fields.Float(string='Fixed Amount')
    amount_percentage = fields.Float(string='Percentage (%)')
    amount_percentage_base = fields.Char(string='Percentage based on')
    amount_python_compute = fields.Text(
        string='Python Code',
        default='result = 0'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner'
    )
    note = fields.Html(string='Description')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    register_id = fields.Many2one(
        'hr.contribution.register',
        string='Contribution Register'
    )
    struct_id = fields.Many2one(
        'hr.payroll.structure',
        string='Salary Structure'
    )

    def _compute_rule(self, localdict):
        """
        Compute the amount of the rule.
        """
        self.ensure_one()
        if self.amount_select == 'fix':
            try:
                return self.amount_fix, float(safe_eval(self.quantity, localdict)), 100.0
            except:
                return self.amount_fix, 1.0, 100.0
        elif self.amount_select == 'percentage':
            try:
                return (
                    float(safe_eval(self.amount_percentage_base, localdict)),
                    float(safe_eval(self.quantity, localdict)),
                    self.amount_percentage
                )
            except:
                return 0, 1.0, self.amount_percentage
        else:
            try:
                safe_eval(self.amount_python_compute, localdict, mode='exec', nocopy=True)
                return float(localdict['result']), 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
            except:
                raise UserError(_('Wrong python code for rule %s') % self.name)

    def _satisfy_condition(self, localdict):
        """
        Check if the rule should be applied.
        """
        self.ensure_one()
        if self.condition_select == 'none':
            return True
        elif self.condition_select == 'range':
            try:
                result = safe_eval(self.condition_range, localdict)
                return self.condition_range_min <= result <= self.condition_range_max
            except:
                return False
        else:
            try:
                safe_eval(self.condition_python, localdict, mode='exec', nocopy=True)
                return localdict.get('result', False)
            except:
                return False
