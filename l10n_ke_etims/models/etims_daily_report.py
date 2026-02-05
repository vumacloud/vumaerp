# -*- coding: utf-8 -*-
"""
eTIMS Daily Reports (X and Z Reports)

Per TIS Technical Specifications v2.0, Sections 15-17:
- X Report: Summary since last Z report (on demand)
- Z Report: End-of-day summary (mandatory daily)

Both include:
- Total sales (NS)
- Total credit notes (NC)
- Tax breakdowns per rate (A-E)
- Items count
- Payment method breakdown
- Discounts
- Number of copies/training/proforma receipts
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class EtimsDailyReport(models.Model):
    """
    eTIMS Daily X and Z Reports.

    Per TIS spec, the TIS must generate:
    - X Report: On-demand summary since last Z report
    - Z Report: End-of-day mandatory summary
    """
    _name = 'etims.daily.report'
    _description = 'eTIMS Daily Report (X/Z)'
    _order = 'report_date desc, id desc'

    name = fields.Char(
        string='Report Number',
        required=True,
        copy=False,
        readonly=True,
        default='/'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    report_type = fields.Selection([
        ('X', 'X Report (Interim)'),
        ('Z', 'Z Report (End of Day)'),
    ], string='Report Type', required=True, default='Z')

    report_date = fields.Date(
        string='Report Date',
        required=True,
        default=fields.Date.today
    )
    report_datetime = fields.Datetime(
        string='Report DateTime',
        required=True,
        default=fields.Datetime.now
    )
    period_start = fields.Datetime(
        string='Period Start',
        help='Start of reporting period (last Z report or day start)'
    )
    period_end = fields.Datetime(
        string='Period End',
        help='End of reporting period'
    )

    # Transaction counts by receipt type
    count_ns = fields.Integer(string='Normal Sales (NS)', default=0)
    count_nc = fields.Integer(string='Normal Credit Notes (NC)', default=0)
    count_cs = fields.Integer(string='Copy Sales (CS)', default=0)
    count_cc = fields.Integer(string='Copy Credit Notes (CC)', default=0)
    count_ts = fields.Integer(string='Training Sales (TS)', default=0)
    count_tc = fields.Integer(string='Training Credit Notes (TC)', default=0)
    count_ps = fields.Integer(string='Proforma Sales (PS)', default=0)

    # Amounts
    total_sales = fields.Monetary(string='Total Sales', currency_field='currency_id')
    total_refunds = fields.Monetary(string='Total Refunds', currency_field='currency_id')
    total_net = fields.Monetary(string='Net Amount', currency_field='currency_id',
                                compute='_compute_net', store=True)
    total_discounts = fields.Monetary(string='Total Discounts', currency_field='currency_id')

    # Tax breakdowns
    taxable_amt_a = fields.Monetary(string='Taxable A (Exempt)', currency_field='currency_id')
    taxable_amt_b = fields.Monetary(string='Taxable B (16%)', currency_field='currency_id')
    taxable_amt_c = fields.Monetary(string='Taxable C (0%)', currency_field='currency_id')
    taxable_amt_d = fields.Monetary(string='Taxable D (Non-VAT)', currency_field='currency_id')
    taxable_amt_e = fields.Monetary(string='Taxable E (8%)', currency_field='currency_id')

    tax_amt_a = fields.Monetary(string='Tax A', currency_field='currency_id')
    tax_amt_b = fields.Monetary(string='Tax B', currency_field='currency_id')
    tax_amt_c = fields.Monetary(string='Tax C', currency_field='currency_id')
    tax_amt_d = fields.Monetary(string='Tax D', currency_field='currency_id')
    tax_amt_e = fields.Monetary(string='Tax E', currency_field='currency_id')

    total_tax = fields.Monetary(string='Total Tax', currency_field='currency_id',
                                compute='_compute_total_tax', store=True)

    # Payment method breakdown
    cash_amount = fields.Monetary(string='Cash', currency_field='currency_id')
    card_amount = fields.Monetary(string='Card', currency_field='currency_id')
    mobile_amount = fields.Monetary(string='Mobile Money', currency_field='currency_id')
    credit_amount = fields.Monetary(string='Credit', currency_field='currency_id')
    other_amount = fields.Monetary(string='Other Payment', currency_field='currency_id')

    # Item counts
    total_items = fields.Integer(string='Total Items Sold')

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('submitted', 'Submitted to eTIMS'),
    ], string='State', default='draft')

    # eTIMS fields
    etims_submitted = fields.Boolean(string='Submitted to eTIMS', default=False)
    etims_response = fields.Text(string='eTIMS Response')

    @api.depends('total_sales', 'total_refunds')
    def _compute_net(self):
        for report in self:
            report.total_net = report.total_sales - report.total_refunds

    @api.depends('tax_amt_a', 'tax_amt_b', 'tax_amt_c', 'tax_amt_d', 'tax_amt_e')
    def _compute_total_tax(self):
        for report in self:
            report.total_tax = (
                report.tax_amt_a + report.tax_amt_b + report.tax_amt_c +
                report.tax_amt_d + report.tax_amt_e
            )

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            report_type = vals.get('report_type', 'Z')
            vals['name'] = self.env['ir.sequence'].next_by_code(
                f'etims.daily.report.{report_type.lower()}'
            ) or f'{report_type}-{fields.Date.today()}'
        return super().create(vals)

    def _get_period_start(self):
        """Get the start of the reporting period (last Z report or day start)."""
        self.ensure_one()
        # Find last Z report for this company
        last_z = self.search([
            ('company_id', '=', self.company_id.id),
            ('report_type', '=', 'Z'),
            ('state', 'in', ['confirmed', 'submitted']),
            ('report_datetime', '<', self.report_datetime),
        ], order='report_datetime desc', limit=1)

        if last_z:
            return last_z.report_datetime
        else:
            # Start of day
            return fields.Datetime.from_string(
                f'{self.report_date} 00:00:00'
            )

    def action_generate_report(self):
        """Generate the report data from transactions."""
        self.ensure_one()

        period_start = self._get_period_start()
        period_end = self.report_datetime

        # Get invoices in period
        invoices = self.env['account.move'].search([
            ('company_id', '=', self.company_id.id),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('etims_submitted', '=', True),
            ('etims_submit_date', '>=', period_start),
            ('etims_submit_date', '<=', period_end),
        ])

        # Get POS orders in period
        pos_orders = self.env['pos.order'].search([
            ('company_id', '=', self.company_id.id),
            ('state', 'in', ['paid', 'done', 'invoiced']),
            ('etims_submitted', '=', True),
            ('etims_submit_date', '>=', period_start),
            ('etims_submit_date', '<=', period_end),
        ])

        # Calculate totals
        vals = {
            'period_start': period_start,
            'period_end': period_end,
            'count_ns': 0,
            'count_nc': 0,
            'total_sales': 0,
            'total_refunds': 0,
            'total_discounts': 0,
            'total_items': 0,
            'taxable_amt_a': 0,
            'taxable_amt_b': 0,
            'taxable_amt_c': 0,
            'taxable_amt_d': 0,
            'taxable_amt_e': 0,
            'tax_amt_a': 0,
            'tax_amt_b': 0,
            'tax_amt_c': 0,
            'tax_amt_d': 0,
            'tax_amt_e': 0,
            'cash_amount': 0,
            'card_amount': 0,
            'mobile_amount': 0,
            'credit_amount': 0,
            'other_amount': 0,
        }

        # Process invoices
        for inv in invoices:
            if inv.move_type == 'out_invoice':
                vals['count_ns'] += 1
                vals['total_sales'] += inv.amount_total
            else:
                vals['count_nc'] += 1
                vals['total_refunds'] += abs(inv.amount_total)

            vals['total_items'] += len(inv.invoice_line_ids.filtered(
                lambda l: not l.display_type
            ))

        # Process POS orders
        for order in pos_orders:
            if order.amount_total >= 0:
                vals['count_ns'] += 1
                vals['total_sales'] += order.amount_total
            else:
                vals['count_nc'] += 1
                vals['total_refunds'] += abs(order.amount_total)

            vals['total_items'] += len(order.lines)

            # Payment breakdown
            for payment in order.payment_ids:
                pm = payment.payment_method_id
                pm_name = pm.name.lower() if pm.name else ''
                amount = payment.amount

                if pm.journal_id and pm.journal_id.type == 'cash':
                    vals['cash_amount'] += amount
                elif any(mm in pm_name for mm in ['mpesa', 'm-pesa', 'mobile', 'airtel']):
                    vals['mobile_amount'] += amount
                elif any(card in pm_name for card in ['card', 'visa', 'mastercard']):
                    vals['card_amount'] += amount
                else:
                    vals['other_amount'] += amount

        vals['state'] = 'confirmed'
        self.write(vals)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Report Generated'),
                'message': _('%s Report generated successfully.') % self.report_type,
                'type': 'success',
            }
        }

    @api.model
    def action_generate_z_report(self):
        """Generate Z report for today (called at end of day)."""
        today = fields.Date.today()

        # Check if Z report already exists for today
        existing = self.search([
            ('company_id', '=', self.env.company.id),
            ('report_type', '=', 'Z'),
            ('report_date', '=', today),
        ], limit=1)

        if existing:
            raise UserError(_('Z Report already exists for today. You can only have one Z report per day.'))

        report = self.create({
            'report_type': 'Z',
            'report_date': today,
            'report_datetime': fields.Datetime.now(),
        })
        return report.action_generate_report()

    @api.model
    def action_generate_x_report(self):
        """Generate X report (interim report on demand)."""
        report = self.create({
            'report_type': 'X',
            'report_date': fields.Date.today(),
            'report_datetime': fields.Datetime.now(),
        })
        return report.action_generate_report()
