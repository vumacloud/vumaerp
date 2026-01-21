# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _description = 'Pay Slip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_from desc, id desc'

    name = fields.Char(
        string='Payslip Name',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    number = fields.Char(
        string='Reference',
        readonly=True,
        copy=False
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    date_from = fields.Date(
        string='Date From',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: fields.Date.today().replace(day=1)
    )
    date_to = fields.Date(
        string='Date To',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: (fields.Date.today().replace(day=1) + relativedelta(months=1, days=-1))
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('cancel', 'Rejected'),
    ], string='Status', default='draft', readonly=True, tracking=True)
    line_ids = fields.One2many(
        'hr.payslip.line',
        'slip_id',
        string='Payslip Lines',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True,
        default=lambda self: self.env.company,
        states={'draft': [('readonly', False)]}
    )
    contract_id = fields.Many2one(
        'hr.contract',
        string='Contract',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    struct_id = fields.Many2one(
        'hr.payroll.structure',
        string='Structure',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    credit_note = fields.Boolean(
        string='Credit Note',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    payslip_run_id = fields.Many2one(
        'hr.payslip.run',
        string='Payslip Batches',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Currency'
    )
    note = fields.Text(string='Internal Note')
    paid = fields.Boolean(string='Made Payment Order', readonly=True)

    @api.onchange('employee_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if self.employee_id and self.date_from and self.date_to:
            contract = self.env['hr.contract'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'open'),
                ('date_start', '<=', self.date_to),
                '|',
                ('date_end', '=', False),
                ('date_end', '>=', self.date_from),
            ], limit=1)
            self.contract_id = contract
            if contract:
                self.struct_id = contract.struct_id
            self.name = _('Salary Slip of %s for %s') % (
                self.employee_id.name,
                self.date_from.strftime('%B %Y')
            )

    def compute_sheet(self):
        """Compute the payslip lines."""
        for payslip in self:
            payslip.line_ids.unlink()
            if not payslip.contract_id or not payslip.struct_id:
                continue

            # Get all rules from structure
            rules = payslip.struct_id.get_all_rules()

            # Build localdict for python evaluation
            localdict = {
                'categories': BrowsableObject({}, self.env),
                'rules': BrowsableObject({}, self.env),
                'payslip': payslip,
                'employee': payslip.employee_id,
                'contract': payslip.contract_id,
                'result': 0,
                'result_qty': 1.0,
                'result_rate': 100.0,
            }

            # Category totals
            category_totals = {}

            # Process rules in sequence order
            for rule in rules.sorted(key=lambda r: r.sequence):
                if not rule._satisfy_condition(localdict):
                    continue

                # Compute the rule
                amount, qty, rate = rule._compute_rule(localdict)
                total = amount * qty * rate / 100

                # Store in localdict
                localdict['rules'].dict[rule.code] = {
                    'total': total,
                    'amount': amount,
                    'quantity': qty,
                }

                # Update category totals
                cat = rule.category_id
                if cat.code not in category_totals:
                    category_totals[cat.code] = 0
                category_totals[cat.code] += total
                localdict['categories'].dict[cat.code] = category_totals[cat.code]

                # Create line
                self.env['hr.payslip.line'].create({
                    'slip_id': payslip.id,
                    'name': rule.name,
                    'code': rule.code,
                    'category_id': rule.category_id.id,
                    'sequence': rule.sequence,
                    'appears_on_payslip': rule.appears_on_payslip,
                    'quantity': qty,
                    'rate': rate,
                    'amount': amount,
                    'total': total,
                    'salary_rule_id': rule.id,
                })

        return True

    def action_payslip_draft(self):
        return self.write({'state': 'draft'})

    def action_payslip_done(self):
        if not self.number:
            for payslip in self:
                payslip.number = self.env['ir.sequence'].next_by_code('salary.slip') or '/'
        return self.write({'state': 'done'})

    def action_payslip_cancel(self):
        return self.write({'state': 'cancel'})

    def action_payslip_verify(self):
        return self.write({'state': 'verify'})


class BrowsableObject(object):
    """Helper for rule evaluation"""
    def __init__(self, dict_vals, env):
        self.dict = dict_vals
        self.env = env

    def __getattr__(self, attr):
        return self.dict.get(attr, 0)


class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _description = 'Payslip Batch'

    name = fields.Char(string='Name', required=True)
    slip_ids = fields.One2many(
        'hr.payslip',
        'payslip_run_id',
        string='Payslips'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('close', 'Close'),
    ], string='Status', default='draft', readonly=True)
    date_start = fields.Date(
        string='Date From',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    date_end = fields.Date(
        string='Date To',
        required=True,
        default=lambda self: (fields.Date.today().replace(day=1) + relativedelta(months=1, days=-1))
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    def action_close(self):
        self.slip_ids.action_payslip_done()
        return self.write({'state': 'close'})

    def action_draft(self):
        return self.write({'state': 'draft'})
