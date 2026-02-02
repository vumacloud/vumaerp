# -*- coding: utf-8 -*-
from odoo import models, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'

    struct_id = fields.Many2one(
        'hr.payroll.structure',
        string='Salary Structure'
    )
