# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # Kenya statutory deduction amounts (computed from rules)
    ke_paye_amount = fields.Float(
        string='PAYE Amount',
        compute='_compute_kenya_deductions',
        store=True,
    )
    ke_shif_amount = fields.Float(
        string='SHIF Amount',
        compute='_compute_kenya_deductions',
        store=True,
        help='SHA Social Health Insurance Fund (replaced NHIF Oct 2024)',
    )
    ke_nssf_amount = fields.Float(
        string='NSSF Amount',
        compute='_compute_kenya_deductions',
        store=True,
    )
    ke_housing_levy_amount = fields.Float(
        string='Housing Levy Amount',
        compute='_compute_kenya_deductions',
        store=True,
    )

    # Relief amounts
    ke_personal_relief = fields.Float(
        string='Personal Relief',
        compute='_compute_kenya_deductions',
        store=True,
    )
    ke_insurance_relief = fields.Float(
        string='Insurance Relief',
        compute='_compute_kenya_deductions',
        store=True,
    )

    @api.depends('line_ids', 'line_ids.total')
    def _compute_kenya_deductions(self):
        for payslip in self:
            lines = {line.code: line.total for line in payslip.line_ids}
            payslip.ke_paye_amount = abs(lines.get('KE_PAYE', 0))
            payslip.ke_shif_amount = abs(lines.get('KE_SHIF', 0))
            payslip.ke_nssf_amount = abs(lines.get('KE_NSSF', 0))
            payslip.ke_housing_levy_amount = abs(lines.get('KE_HOUSING', 0))
            payslip.ke_personal_relief = lines.get('KE_PERSONAL_RELIEF', 0)
            payslip.ke_insurance_relief = lines.get('KE_INSURANCE_RELIEF', 0)


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    ke_statutory_type = fields.Selection([
        ('paye', 'PAYE'),
        ('shif', 'SHIF'),
        ('nssf', 'NSSF'),
        ('housing', 'Housing Levy'),
    ], string='Kenya Statutory Type')
