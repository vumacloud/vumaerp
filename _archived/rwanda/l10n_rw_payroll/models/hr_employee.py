# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Rwanda-specific identification
    rw_national_id = fields.Char(
        string='National ID',
        help='Rwanda National ID number (16 digits)'
    )
    rssb_number = fields.Char(
        string='RSSB Number',
        help='Rwanda Social Security Board member number'
    )
    tin_number = fields.Char(
        string='TIN',
        help='Tax Identification Number issued by RRA'
    )

    # CBHI Information
    cbhi_category = fields.Selection([
        ('1', 'Category 1 - Poorest'),
        ('2', 'Category 2 - Poor'),
        ('3', 'Category 3 - Middle'),
        ('4', 'Category 4 - Upper'),
    ], string='CBHI Category', default='3',
        help='Community Based Health Insurance category based on Ubudehe classification')
    cbhi_card_number = fields.Char(
        string='CBHI Card Number',
        help='Mutuelle de Santé card number'
    )

    # Bank Information
    bank_account_number = fields.Char(string='Bank Account Number')
    bank_id = fields.Many2one('res.bank', string='Bank')

    @api.constrains('rw_national_id')
    def _check_national_id(self):
        for employee in self:
            if employee.rw_national_id:
                # Remove spaces and validate
                nid = employee.rw_national_id.replace(' ', '')
                if len(nid) != 16 or not nid.isdigit():
                    pass  # Warning only, don't block
