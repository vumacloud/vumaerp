# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrPayslipLine(models.Model):
    _name = 'hr.payslip.line'
    _description = 'Payslip Line'
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    slip_id = fields.Many2one(
        'hr.payslip',
        string='Pay Slip',
        required=True,
        ondelete='cascade'
    )
    employee_id = fields.Many2one(
        related='slip_id.employee_id',
        string='Employee',
        store=True
    )
    salary_rule_id = fields.Many2one(
        'hr.salary.rule',
        string='Rule'
    )
    category_id = fields.Many2one(
        'hr.salary.rule.category',
        string='Category',
        required=True
    )
    sequence = fields.Integer(string='Sequence', default=5)
    quantity = fields.Float(string='Quantity', default=1.0)
    rate = fields.Float(string='Rate (%)', default=100.0)
    amount = fields.Float(string='Amount')
    total = fields.Float(
        string='Total',
        compute='_compute_total',
        store=True
    )
    appears_on_payslip = fields.Boolean(string='Appears on Payslip', default=True)
    company_id = fields.Many2one(
        related='slip_id.company_id',
        string='Company',
        store=True
    )
    date_from = fields.Date(related='slip_id.date_from', store=True)
    date_to = fields.Date(related='slip_id.date_to', store=True)
    contract_id = fields.Many2one(related='slip_id.contract_id', store=True)

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        for line in self:
            line.total = line.quantity * line.amount * line.rate / 100
