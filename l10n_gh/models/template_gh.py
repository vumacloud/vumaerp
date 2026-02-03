# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, models

from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('gh')
    def _get_gh_template_data(self):
        return {
            'name': _('Ghana'),
            'code_digits': '6',
            'property_account_receivable_id': 'gh_110100',
            'property_account_payable_id': 'gh_210100',
            'property_account_expense_categ_id': 'gh_510100',
            'property_account_income_categ_id': 'gh_410100',
        }

    @template('gh', 'res.company')
    def _get_gh_res_company(self):
        return {
            self.env.company.id: {
                'account_fiscal_country_id': 'base.gh',
                'account_default_pos_receivable_account_id': 'gh_110200',
                'income_currency_exchange_account_id': 'gh_420100',
                'expense_currency_exchange_account_id': 'gh_520100',
            },
        }

    @template('gh', 'account.tax.group')
    def _get_gh_account_tax_group(self):
        return {
            'tax_group_vat_15': {
                'name': _('VAT 15%'),
                'sequence': 10,
                'country_id': 'base.gh',
            },
            'tax_group_vat_3': {
                'name': _('VAT 3% (Flat Rate)'),
                'sequence': 11,
                'country_id': 'base.gh',
            },
            'tax_group_nhil': {
                'name': _('NHIL 2.5%'),
                'sequence': 20,
                'country_id': 'base.gh',
            },
            'tax_group_getfund': {
                'name': _('GETFund 2.5%'),
                'sequence': 21,
                'country_id': 'base.gh',
            },
            'tax_group_exempt': {
                'name': _('VAT Exempt'),
                'sequence': 30,
                'country_id': 'base.gh',
            },
        }

    @template('gh', 'account.tax')
    def _get_gh_account_tax(self):
        return {
            'gh_vat_sale_15': {
                'name': _('VAT 15% (Sales)'),
                'description': 'VAT 15%',
                'amount': 15.0,
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'tax_group_id': 'tax_group_vat_15',
                'invoice_repartition_line_ids': [
                    {
                        'repartition_type': 'base',
                        'tag_ids': [],
                    },
                    {
                        'repartition_type': 'tax',
                        'account_id': 'gh_230100',
                        'tag_ids': [],
                    },
                ],
                'refund_repartition_line_ids': [
                    {
                        'repartition_type': 'base',
                        'tag_ids': [],
                    },
                    {
                        'repartition_type': 'tax',
                        'account_id': 'gh_230100',
                        'tag_ids': [],
                    },
                ],
            },
            'gh_vat_purchase_15': {
                'name': _('VAT 15% (Purchases)'),
                'description': 'VAT 15%',
                'amount': 15.0,
                'amount_type': 'percent',
                'type_tax_use': 'purchase',
                'tax_group_id': 'tax_group_vat_15',
                'invoice_repartition_line_ids': [
                    {
                        'repartition_type': 'base',
                        'tag_ids': [],
                    },
                    {
                        'repartition_type': 'tax',
                        'account_id': 'gh_130100',
                        'tag_ids': [],
                    },
                ],
                'refund_repartition_line_ids': [
                    {
                        'repartition_type': 'base',
                        'tag_ids': [],
                    },
                    {
                        'repartition_type': 'tax',
                        'account_id': 'gh_130100',
                        'tag_ids': [],
                    },
                ],
            },
            'gh_nhil_sale': {
                'name': _('NHIL 2.5% (Sales)'),
                'description': 'NHIL 2.5%',
                'amount': 2.5,
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'tax_group_id': 'tax_group_nhil',
                'invoice_repartition_line_ids': [
                    {
                        'repartition_type': 'base',
                        'tag_ids': [],
                    },
                    {
                        'repartition_type': 'tax',
                        'account_id': 'gh_230200',
                        'tag_ids': [],
                    },
                ],
                'refund_repartition_line_ids': [
                    {
                        'repartition_type': 'base',
                        'tag_ids': [],
                    },
                    {
                        'repartition_type': 'tax',
                        'account_id': 'gh_230200',
                        'tag_ids': [],
                    },
                ],
            },
            'gh_nhil_purchase': {
                'name': _('NHIL 2.5% (Purchases)'),
                'description': 'NHIL 2.5%',
                'amount': 2.5,
                'amount_type': 'percent',
                'type_tax_use': 'purchase',
                'tax_group_id': 'tax_group_nhil',
                'invoice_repartition_line_ids': [
                    {
                        'repartition_type': 'base',
                        'tag_ids': [],
                    },
                    {
                        'repartition_type': 'tax',
                        'account_id': 'gh_130200',
                        'tag_ids': [],
                    },
                ],
                'refund_repartition_line_ids': [
                    {
                        'repartition_type': 'base',
                        'tag_ids': [],
                    },
                    {
                        'repartition_type': 'tax',
                        'account_id': 'gh_130200',
                        'tag_ids': [],
                    },
                ],
            },
            'gh_getfund_sale': {
                'name': _('GETFund 2.5% (Sales)'),
                'description': 'GETFund 2.5%',
                'amount': 2.5,
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'tax_group_id': 'tax_group_getfund',
                'invoice_repartition_line_ids': [
                    {
                        'repartition_type': 'base',
                        'tag_ids': [],
                    },
                    {
                        'repartition_type': 'tax',
                        'account_id': 'gh_230300',
                        'tag_ids': [],
                    },
                ],
                'refund_repartition_line_ids': [
                    {
                        'repartition_type': 'base',
                        'tag_ids': [],
                    },
                    {
                        'repartition_type': 'tax',
                        'account_id': 'gh_230300',
                        'tag_ids': [],
                    },
                ],
            },
            'gh_getfund_purchase': {
                'name': _('GETFund 2.5% (Purchases)'),
                'description': 'GETFund 2.5%',
                'amount': 2.5,
                'amount_type': 'percent',
                'type_tax_use': 'purchase',
                'tax_group_id': 'tax_group_getfund',
                'invoice_repartition_line_ids': [
                    {
                        'repartition_type': 'base',
                        'tag_ids': [],
                    },
                    {
                        'repartition_type': 'tax',
                        'account_id': 'gh_130300',
                        'tag_ids': [],
                    },
                ],
                'refund_repartition_line_ids': [
                    {
                        'repartition_type': 'base',
                        'tag_ids': [],
                    },
                    {
                        'repartition_type': 'tax',
                        'account_id': 'gh_130300',
                        'tag_ids': [],
                    },
                ],
            },
            'gh_vat_sale_3_flat': {
                'name': _('VAT 3% Flat Rate (Sales)'),
                'description': 'VAT 3%',
                'amount': 3.0,
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'tax_group_id': 'tax_group_vat_3',
                'invoice_repartition_line_ids': [
                    {
                        'repartition_type': 'base',
                        'tag_ids': [],
                    },
                    {
                        'repartition_type': 'tax',
                        'account_id': 'gh_230100',
                        'tag_ids': [],
                    },
                ],
                'refund_repartition_line_ids': [
                    {
                        'repartition_type': 'base',
                        'tag_ids': [],
                    },
                    {
                        'repartition_type': 'tax',
                        'account_id': 'gh_230100',
                        'tag_ids': [],
                    },
                ],
            },
            'gh_vat_exempt_sale': {
                'name': _('VAT Exempt (Sales)'),
                'description': 'Exempt',
                'amount': 0.0,
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'tax_group_id': 'tax_group_exempt',
            },
            'gh_vat_exempt_purchase': {
                'name': _('VAT Exempt (Purchases)'),
                'description': 'Exempt',
                'amount': 0.0,
                'amount_type': 'percent',
                'type_tax_use': 'purchase',
                'tax_group_id': 'tax_group_exempt',
            },
        }
