# -*- coding: utf-8 -*-
from odoo import models, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # Rwanda Payroll Configuration
    rw_tax_exempt = fields.Boolean(
        string='Tax Exempt',
        default=False,
        help='Check if this employee is exempt from PAYE'
    )
    rw_rssb_exempt = fields.Boolean(
        string='RSSB Exempt',
        default=False,
        help='Check if exempt from RSSB contributions (e.g., foreign workers under 5 years)'
    )

    # Allowances (common in Rwanda)
    housing_allowance = fields.Monetary(
        string='Housing Allowance',
        currency_field='currency_id',
        help='Monthly housing allowance'
    )
    transport_allowance = fields.Monetary(
        string='Transport Allowance',
        currency_field='currency_id',
        help='Monthly transport allowance'
    )
    responsibility_allowance = fields.Monetary(
        string='Responsibility Allowance',
        currency_field='currency_id',
        help='Monthly responsibility allowance'
    )
    communication_allowance = fields.Monetary(
        string='Communication Allowance',
        currency_field='currency_id',
        help='Monthly communication/airtime allowance'
    )
    other_allowances = fields.Monetary(
        string='Other Allowances',
        currency_field='currency_id',
        help='Other taxable allowances'
    )

    # Benefits
    medical_insurance = fields.Monetary(
        string='Medical Insurance (Employer)',
        currency_field='currency_id',
        help='Employer-paid medical insurance beyond CBHI'
    )
