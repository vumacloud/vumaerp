# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # KRA e-TIMS Fields
    kra_item_class_code = fields.Char(
        string='KRA Item Class Code',
        help='e-TIMS Item Classification Code (e.g., 5020230500)',
        default='5020230500'
    )
    
    kra_item_type_code = fields.Selection([
        ('1', 'Raw Material'),
        ('2', 'Finished Product'),
        ('3', 'Service'),
    ], string='Item Type', default='2',
       help='Type of item for e-TIMS classification')
    
    kra_origin_country_code = fields.Char(
        string='Origin Country Code',
        default='KE',
        help='ISO country code (e.g., KE for Kenya)'
    )
    
    kra_package_unit_code = fields.Char(
        string='Package Unit Code',
        default='NT',
        help='Package unit code (e.g., BX=Box, NT=Not Applicable)'
    )
    
    kra_tax_type_code = fields.Selection([
        ('A', 'VAT 0% (Exempt)'),
        ('B', 'VAT 16% (Standard)'),
        ('C', 'VAT 8% (Reduced)'),
        ('D', 'No Tax'),
    ], string='Tax Type', default='B',
       help='Tax type for e-TIMS')
    
    kra_registered = fields.Boolean(
        string='Registered in e-TIMS',
        readonly=True,
        copy=False
    )
    
    kra_registration_date = fields.Datetime(
        string='e-TIMS Registration Date',
        readonly=True,
        copy=False
    )
    
    def action_register_etims(self):
        """Register product with KRA e-TIMS"""
        self.ensure_one()
        
        if not self.env.company.kra_etims_enabled:
            raise UserError(_('KRA e-TIMS is not enabled for this company.'))
        
        api = self.env['kra.etims.api']
        
        try:
            result = api.save_item(self)
            
            self.write({
                'kra_registered': True,
                'kra_registration_date': fields.Datetime.now(),
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Product registered with KRA e-TIMS successfully'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(_('Product registration failed: %s') % str(e))
    
    @api.model
    def create(self, vals):
        """Auto-register product if enabled"""
        product = super(ProductTemplate, self).create(vals)
        
        if self.env.company.kra_etims_enabled and self.env.company.kra_etims_auto_submit:
            try:
                product.action_register_etims()
            except:
                pass  # Don't block creation if registration fails
        
        return product


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    kra_registered = fields.Boolean(
        related='product_tmpl_id.kra_registered',
        readonly=True
    )


class UomUom(models.Model):
    _inherit = 'uom.uom'
    
    kra_unit_code = fields.Char(
        string='KRA Unit Code',
        help='Unit code for e-TIMS (e.g., U=Unit, KG=Kilogram, L=Liter)'
    )
