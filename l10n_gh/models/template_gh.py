# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('gh')
    def _get_gh_template_data(self):
        return {
            'name': _('Ghana'),
            'code_digits': '6',
            'property_account_receivable_id': 'gh_1100',
            'property_account_payable_id': 'gh_2100',
            'property_account_expense_categ_id': 'gh_5100',
            'property_account_income_categ_id': 'gh_4100',
        }

    @template('gh', 'res.company')
    def _get_gh_res_company(self):
        return {
            self.env.company.id: {
                'account_fiscal_country_id': 'base.gh',
                'income_currency_exchange_account_id': 'gh_4200',
                'expense_currency_exchange_account_id': 'gh_5200',
                'account_sale_tax_id': 'gh_vat_sale_15',
                'account_purchase_tax_id': 'gh_vat_purchase_15',
            },
        }

    @template('gh', 'account.tax.group')
    def _get_gh_account_tax_group(self):
        return {
            'gh_tax_group_vat_15': {
                'name': _('VAT 15%'),
                'sequence': 10,
                'country_id': 'base.gh',
            },
            'gh_tax_group_nhil': {
                'name': _('NHIL 2.5%'),
                'sequence': 20,
                'country_id': 'base.gh',
            },
            'gh_tax_group_getfund': {
                'name': _('GETFund 2.5%'),
                'sequence': 21,
                'country_id': 'base.gh',
            },
            'gh_tax_group_vat_3': {
                'name': _('VAT 3% Flat Rate'),
                'sequence': 30,
                'country_id': 'base.gh',
            },
            'gh_tax_group_exempt': {
                'name': _('VAT Exempt'),
                'sequence': 40,
                'country_id': 'base.gh',
            },
            'gh_tax_group_zero': {
                'name': _('Zero Rated'),
                'sequence': 41,
                'country_id': 'base.gh',
            },
        }

    @template('gh', 'account.tax')
    def _get_gh_account_tax(self):
        return {
            # ===================
            # SALES TAXES
            # ===================
            'gh_vat_sale_15': {
                'name': _('VAT 15% (Sales)'),
                'description': '15%',
                'amount': 15.0,
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'tax_group_id': 'gh_tax_group_vat_15',
                'sequence': 10,
            },
            'gh_nhil_sale': {
                'name': _('NHIL 2.5% (Sales)'),
                'description': '2.5%',
                'amount': 2.5,
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'tax_group_id': 'gh_tax_group_nhil',
                'sequence': 20,
            },
            'gh_getfund_sale': {
                'name': _('GETFund 2.5% (Sales)'),
                'description': '2.5%',
                'amount': 2.5,
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'tax_group_id': 'gh_tax_group_getfund',
                'sequence': 21,
            },
            'gh_vat_sale_3_flat': {
                'name': _('VAT 3% Flat Rate (Sales)'),
                'description': '3%',
                'amount': 3.0,
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'tax_group_id': 'gh_tax_group_vat_3',
                'sequence': 30,
            },
            'gh_vat_sale_exempt': {
                'name': _('VAT Exempt (Sales)'),
                'description': '0%',
                'amount': 0.0,
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'tax_group_id': 'gh_tax_group_exempt',
                'sequence': 40,
            },
            'gh_vat_sale_zero': {
                'name': _('Zero Rated (Sales)'),
                'description': '0%',
                'amount': 0.0,
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'tax_group_id': 'gh_tax_group_zero',
                'sequence': 41,
            },
            # ===================
            # PURCHASE TAXES
            # ===================
            'gh_vat_purchase_15': {
                'name': _('VAT 15% (Purchases)'),
                'description': '15%',
                'amount': 15.0,
                'amount_type': 'percent',
                'type_tax_use': 'purchase',
                'tax_group_id': 'gh_tax_group_vat_15',
                'sequence': 10,
            },
            'gh_nhil_purchase': {
                'name': _('NHIL 2.5% (Purchases)'),
                'description': '2.5%',
                'amount': 2.5,
                'amount_type': 'percent',
                'type_tax_use': 'purchase',
                'tax_group_id': 'gh_tax_group_nhil',
                'sequence': 20,
            },
            'gh_getfund_purchase': {
                'name': _('GETFund 2.5% (Purchases)'),
                'description': '2.5%',
                'amount': 2.5,
                'amount_type': 'percent',
                'type_tax_use': 'purchase',
                'tax_group_id': 'gh_tax_group_getfund',
                'sequence': 21,
            },
            'gh_vat_purchase_exempt': {
                'name': _('VAT Exempt (Purchases)'),
                'description': '0%',
                'amount': 0.0,
                'amount_type': 'percent',
                'type_tax_use': 'purchase',
                'tax_group_id': 'gh_tax_group_exempt',
                'sequence': 40,
            },
            'gh_vat_purchase_zero': {
                'name': _('Zero Rated (Purchases)'),
                'description': '0%',
                'amount': 0.0,
                'amount_type': 'percent',
                'type_tax_use': 'purchase',
                'tax_group_id': 'gh_tax_group_zero',
                'sequence': 41,
            },
        }
