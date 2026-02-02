# -*- coding: utf-8 -*-
from odoo import models, fields


class HrContributionRegister(models.Model):
    _name = 'hr.contribution.register'
    _description = 'Contribution Register'

    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner'
    )
    note = fields.Text(string='Description')
