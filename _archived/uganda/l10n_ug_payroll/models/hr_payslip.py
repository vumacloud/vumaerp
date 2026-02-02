# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # Uganda statutory deduction amounts
    ug_paye_amount = fields.Float(
        string='PAYE Amount',
        compute='_compute_uganda_deductions',
        store=True,
    )
    ug_nssf_employee = fields.Float(
        string='NSSF (Employee)',
        compute='_compute_uganda_deductions',
        store=True,
    )
    ug_nssf_employer = fields.Float(
        string='NSSF (Employer)',
        compute='_compute_uganda_deductions',
        store=True,
    )
    ug_lst_amount = fields.Float(
        string='LST Amount',
        compute='_compute_uganda_deductions',
        store=True,
    )

    @api.depends('line_ids', 'line_ids.total')
    def _compute_uganda_deductions(self):
        for payslip in self:
            lines = {line.code: line.total for line in payslip.line_ids}
            payslip.ug_paye_amount = abs(lines.get('UG_PAYE', 0))
            payslip.ug_nssf_employee = abs(lines.get('UG_NSSF', 0))
            payslip.ug_nssf_employer = lines.get('UG_NSSF_ER', 0)
            payslip.ug_lst_amount = abs(lines.get('UG_LST', 0))


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    ug_statutory_type = fields.Selection([
        ('paye', 'PAYE'),
        ('nssf', 'NSSF'),
        ('lst', 'LST'),
    ], string='Uganda Statutory Type')
