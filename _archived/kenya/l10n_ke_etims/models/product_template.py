# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # eTIMS Fields
    etims_registered = fields.Boolean(
        string='Registered with eTIMS',
        default=False,
        copy=False,
    )
    etims_item_code = fields.Char(
        string='eTIMS Item Code',
        copy=False,
        help='Unique item code assigned by eTIMS',
    )
    etims_item_class_id = fields.Many2one(
        'etims.item.class',
        string='eTIMS Classification',
        help='eTIMS Item Classification Code',
    )
    etims_origin_country_id = fields.Many2one(
        'res.country',
        string='Country of Origin',
        help='Country of origin for eTIMS reporting',
    )
    etims_pkg_unit_code = fields.Char(
        string='Packaging Unit Code',
        default='NT',
        help='eTIMS Packaging Unit Code (e.g., CT=Carton, BX=Box, NT=No Packaging)',
    )
    etims_qty_unit_code = fields.Char(
        string='Quantity Unit Code',
        default='U',
        help='eTIMS Quantity Unit Code (e.g., KG, LT, U=Unit)',
    )
    etims_product_type = fields.Selection([
        ('1', 'Raw Material'),
        ('2', 'Finished Product'),
        ('3', 'Service'),
    ], string='eTIMS Product Type', default='2')

    etims_tax_type = fields.Selection([
        ('A', 'A - Exempt'),
        ('B', 'B - Standard Rate (16%)'),
        ('C', 'C - Reduced Rate (8%)'),
        ('D', 'D - Zero Rate'),
        ('E', 'E - Exempt'),
    ], string='eTIMS Tax Type', default='B')

    etims_insurance_applicable = fields.Boolean(
        string='Insurance Applicable',
        default=False,
    )
    etims_batch_applicable = fields.Boolean(
        string='Batch/Lot Applicable',
        default=False,
    )
    etims_registration_date = fields.Datetime(
        string='eTIMS Registration Date',
        copy=False,
        readonly=True,
    )

    def action_register_etims(self):
        """Register product with KRA eTIMS."""
        self.ensure_one()

        if self.etims_registered:
            raise UserError(_('This product is already registered with eTIMS.'))

        config = self.env['etims.config'].get_active_config()
        if not config:
            raise UserError(_('eTIMS is not configured. Please configure eTIMS settings first.'))

        api = self.env['etims.api']

        # Prepare item data
        item_data = self._prepare_etims_item_data(config)

        try:
            response = api.save_item(config, item_data)

            if response.get('resultCd') == '000':
                result_data = response.get('data', {})
                self.write({
                    'etims_registered': True,
                    'etims_item_code': result_data.get('itemCd') or self.default_code or str(self.id),
                    'etims_registration_date': fields.Datetime.now(),
                })
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Product registered with eTIMS successfully.'),
                        'type': 'success',
                    }
                }
            else:
                error_msg = response.get('resultMsg', 'Unknown error')
                raise UserError(_('eTIMS Error: %s') % error_msg)

        except Exception as e:
            _logger.error('eTIMS item registration error: %s', str(e))
            raise UserError(_('Failed to register with eTIMS: %s') % str(e))

    def _prepare_etims_item_data(self, config):
        """Prepare item data for eTIMS API."""
        self.ensure_one()

        return {
            'tin': config.tin,
            'bhfId': config.branch_id or '00',
            'itemCd': self.default_code or str(self.id),
            'itemClsCd': self.etims_item_class_id.code if self.etims_item_class_id else '',
            'itemTyCd': self.etims_product_type or '2',
            'itemNm': self.name,
            'itemStdNm': self.name,
            'orgnNatCd': self.etims_origin_country_id.code if self.etims_origin_country_id else 'KE',
            'pkgUnitCd': self.etims_pkg_unit_code or 'NT',
            'qtyUnitCd': self.etims_qty_unit_code or 'U',
            'taxTyCd': self.etims_tax_type or 'B',
            'btchNo': '',
            'bcd': self.barcode or '',
            'dftPrc': self.list_price,
            'grpPrcL1': self.list_price,
            'grpPrcL2': self.list_price,
            'grpPrcL3': self.list_price,
            'grpPrcL4': self.list_price,
            'grpPrcL5': self.list_price,
            'addInfo': self.description or '',
            'sftyQty': 0,
            'isrcAplcbYn': 'Y' if self.etims_insurance_applicable else 'N',
            'useYn': 'Y' if self.active else 'N',
            'regrId': self.env.user.login,
            'regrNm': self.env.user.name,
            'modrId': self.env.user.login,
            'modrNm': self.env.user.name,
        }

    def action_bulk_register_etims(self):
        """Bulk register selected products with eTIMS."""
        products_to_register = self.filtered(lambda p: not p.etims_registered)

        if not products_to_register:
            raise UserError(_('All selected products are already registered with eTIMS.'))

        config = self.env['etims.config'].get_active_config()
        if not config:
            raise UserError(_('eTIMS is not configured. Please configure eTIMS settings first.'))

        success_count = 0
        failed_count = 0

        for product in products_to_register:
            try:
                product.action_register_etims()
                success_count += 1
            except Exception as e:
                _logger.warning('Failed to register product %s: %s', product.name, str(e))
                failed_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Registration Complete'),
                'message': _('Registered: %d, Failed: %d') % (success_count, failed_count),
                'type': 'success' if failed_count == 0 else 'warning',
            }
        }


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_register_etims(self):
        """Register product variant with eTIMS."""
        return self.product_tmpl_id.action_register_etims()
