# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    # KRA e-TIMS Fields
    kra_invoice_no = fields.Integer(
        string='e-TIMS Invoice Number',
        readonly=True,
        copy=False,
        help='Invoice number assigned by e-TIMS'
    )
    
    kra_invoice_counter = fields.Integer(
        string='Invoice Counter',
        readonly=True,
        copy=False
    )
    
    kra_submission_status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='e-TIMS Status', default='draft', copy=False)
    
    kra_submission_date = fields.Datetime(
        string='Submission Date',
        readonly=True,
        copy=False
    )
    
    kra_internal_data = fields.Char(
        string='Internal Data',
        readonly=True,
        copy=False,
        help='Internal data returned by e-TIMS'
    )
    
    kra_receipt_signature = fields.Char(
        string='Receipt Signature',
        readonly=True,
        copy=False,
        help='Digital signature from e-TIMS'
    )
    
    kra_sdc_datetime = fields.Char(
        string='SDC DateTime',
        readonly=True,
        copy=False,
        help='SDC Date and Time from e-TIMS'
    )
    
    kra_cu_serial = fields.Char(
        string='CU Serial Number',
        readonly=True,
        copy=False,
        help='Control Unit Serial Number'
    )
    
    kra_payment_type = fields.Selection([
        ('01', 'Cash'),
        ('02', 'Credit'),
        ('03', 'Card'),
        ('04', 'Mobile Money'),
    ], string='Payment Type', default='01',
       help='Payment type for e-TIMS')
    
    kra_qr_code = fields.Char(
        string='QR Code',
        compute='_compute_kra_qr_code',
        store=True,
        help='QR code data for the invoice'
    )
    
    @api.depends('kra_internal_data', 'kra_invoice_no')
    def _compute_kra_qr_code(self):
        """Generate QR code data"""
        for invoice in self:
            if invoice.kra_internal_data and invoice.kra_invoice_no:
                # QR code format: InvoiceNo|InternalData|TIN|DateTime
                invoice.kra_qr_code = f"{invoice.kra_invoice_no}|{invoice.kra_internal_data}|{self.env.company.kra_etims_tin}|{invoice.kra_sdc_datetime}"
            else:
                invoice.kra_qr_code = False
    
    def action_post(self):
        """Override to auto-submit to e-TIMS if enabled"""
        # In v18, action_post() doesn't return a value
        super(AccountMove, self).action_post()
        
        for invoice in self:
            if invoice.move_type in ['out_invoice', 'out_refund']:
                if self.env.company.kra_etims_enabled and self.env.company.kra_etims_auto_submit:
                    try:
                        invoice.action_submit_etims()
                    except Exception as e:
                        # Log error but don't block posting
                        invoice.message_post(
                            body=_('Failed to auto-submit to e-TIMS: %s') % str(e)
                        )
    
    def action_submit_etims(self):
        """Submit invoice to KRA e-TIMS"""
        self.ensure_one()
        
        if self.move_type not in ['out_invoice', 'out_refund']:
            raise UserError(_('Only customer invoices and credit notes can be submitted to e-TIMS.'))
        
        if self.state != 'posted':
            raise UserError(_('Only posted invoices can be submitted to e-TIMS.'))
        
        if self.kra_submission_status == 'submitted':
            raise UserError(_('This invoice has already been submitted to e-TIMS.'))
        
        if not self.env.company.kra_etims_enabled:
            raise UserError(_('KRA e-TIMS is not enabled for this company.'))
        
        # Validate invoice lines have products
        for line in self.invoice_line_ids:
            if not line.display_type and not line.product_id:
                raise UserError(_('All invoice lines must have a product assigned.'))
        
        # Get next invoice counter
        if not self.kra_invoice_counter:
            counter = self.env.company.get_next_kra_invoice_number()
            self.kra_invoice_counter = counter
        
        # Submit to e-TIMS
        api = self.env['kra.etims.api']
        
        try:
            result = api.save_sales_invoice(self)
            
            self.message_post(
                body=_('Invoice submitted to KRA e-TIMS successfully.<br/>Invoice No: %s<br/>DateTime: %s') % (
                    self.kra_invoice_no, self.kra_sdc_datetime
                )
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Invoice submitted to KRA e-TIMS successfully'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            self.kra_submission_status = 'rejected'
            self.message_post(
                body=_('Failed to submit to KRA e-TIMS: %s') % str(e)
            )
            raise UserError(_('Failed to submit invoice to e-TIMS: %s') % str(e))
    
    def action_retrieve_etims_status(self):
        """Retrieve invoice status from e-TIMS"""
        self.ensure_one()
        
        if not self.kra_invoice_no:
            raise UserError(_('This invoice has not been submitted to e-TIMS yet.'))
        
        api = self.env['kra.etims.api']
        
        try:
            result = api.select_invoice(self.kra_invoice_no)
            
            # Update status based on response
            # You can extend this based on actual API response
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Status retrieved successfully'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(_('Failed to retrieve status: %s') % str(e))
    
    def button_reset_to_draft(self):
        """Prevent setting to draft if submitted to e-TIMS"""
        for invoice in self:
            if invoice.kra_submission_status == 'submitted':
                raise UserError(_('Cannot reset to draft an invoice that has been submitted to e-TIMS.'))
        
        return super(AccountMove, self).button_reset_to_draft()
    
    def button_cancel(self):
        """Handle cancellation for e-TIMS submitted invoices"""
        for invoice in self:
            if invoice.kra_submission_status == 'submitted':
                # In a real implementation, you would need to call the cancellation API
                invoice.message_post(
                    body=_('Warning: This invoice was submitted to e-TIMS. You may need to manually cancel it in the e-TIMS system.')
                )
        
        return super(AccountMove, self).button_cancel()


class AccountTax(models.Model):
    _inherit = 'account.tax'
    
    kra_tax_type_code = fields.Selection([
        ('A', 'VAT 0% (Exempt)'),
        ('B', 'VAT 16% (Standard)'),
        ('C', 'VAT 8% (Reduced)'),
        ('D', 'No Tax'),
    ], string='KRA Tax Type',
       help='Tax type code for e-TIMS')
