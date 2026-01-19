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
    ke_nhif_amount = fields.Float(
        string='NHIF Amount',
        compute='_compute_kenya_deductions',
        store=True,
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
            payslip.ke_nhif_amount = abs(lines.get('KE_NHIF', 0))
            payslip.ke_nssf_amount = abs(lines.get('KE_NSSF', 0))
            payslip.ke_housing_levy_amount = abs(lines.get('KE_HOUSING', 0))
            payslip.ke_personal_relief = lines.get('KE_PERSONAL_RELIEF', 0)
            payslip.ke_insurance_relief = lines.get('KE_INSURANCE_RELIEF', 0)

    def get_kenya_statutory_values(self):
        """Get Kenya statutory calculation values for use in salary rules."""
        self.ensure_one()
        contract = self.contract_id

        # Get configuration
        config = self.env['kenya.statutory.config'].get_config(self.company_id)

        # Calculate gross salary
        gross = contract.wage
        if hasattr(contract, 'ke_house_allowance'):
            gross += contract.ke_house_allowance or 0
        if hasattr(contract, 'ke_transport_allowance'):
            gross += contract.ke_transport_allowance or 0
        if hasattr(contract, 'ke_medical_allowance'):
            gross += contract.ke_medical_allowance or 0
        if hasattr(contract, 'ke_other_allowances'):
            gross += contract.ke_other_allowances or 0

        # NHIF
        nhif = self.env['kenya.nhif.rate'].get_contribution(gross)

        # NSSF
        if contract.ke_pension_opt_out if hasattr(contract, 'ke_pension_opt_out') else False:
            nssf = 0
        else:
            nssf = config.calculate_nssf(gross)

        # Housing Levy
        housing_levy = config.calculate_housing_levy(gross)

        # Taxable income (before reliefs)
        taxable = gross - nssf - (contract.ke_private_pension if hasattr(contract, 'ke_private_pension') else 0)

        # PAYE (before reliefs)
        paye_gross = self.env['kenya.paye.tax.band'].calculate_paye(taxable)

        # Reliefs
        personal_relief = config.personal_relief
        insurance_relief = config.calculate_insurance_relief(nhif)

        # Mortgage relief (max 25,000/month or 300,000/year)
        mortgage_relief = 0
        if hasattr(contract, 'ke_mortgage_interest'):
            mortgage_relief = min(contract.ke_mortgage_interest * 0.15, 25000 * 0.15)

        # Net PAYE
        total_relief = personal_relief + insurance_relief + mortgage_relief
        paye_net = max(0, paye_gross - total_relief)

        return {
            'gross': gross,
            'nhif': nhif,
            'nssf': nssf,
            'housing_levy': housing_levy,
            'taxable_income': taxable,
            'paye_gross': paye_gross,
            'personal_relief': personal_relief,
            'insurance_relief': insurance_relief,
            'mortgage_relief': mortgage_relief,
            'paye_net': paye_net,
        }


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    ke_statutory_type = fields.Selection([
        ('paye', 'PAYE'),
        ('nhif', 'NHIF'),
        ('nssf', 'NSSF'),
        ('housing', 'Housing Levy'),
    ], string='Kenya Statutory Type')
