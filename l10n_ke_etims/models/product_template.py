# -*- coding: utf-8 -*-
"""
Product eTIMS Integration

Per KRA requirements, products must be registered with eTIMS before they
can be sold or included in stock movements. Each product needs:
- A valid UNSPSC classification code
- Unit codes for packaging and quantity
- Tax type classification
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # eTIMS Registration Status
    l10n_ke_etims_registered = fields.Boolean(
        string='Registered with eTIMS',
        default=False,
        copy=False,
        help='Indicates if this product has been registered with KRA eTIMS',
    )
    l10n_ke_etims_item_code = fields.Char(
        string='eTIMS Item Code',
        copy=False,
        help='Unique item code assigned by/to eTIMS',
    )
    l10n_ke_etims_registration_date = fields.Datetime(
        string='eTIMS Registration Date',
        copy=False,
        readonly=True,
    )

    # UNSPSC Classification - Required for eTIMS
    l10n_ke_item_class_id = fields.Many2one(
        'etims.item.class',
        string='UNSPSC Classification',
        help='UNSPSC Item Classification Code required by KRA',
    )

    # Unit Codes
    l10n_ke_pkg_unit_code = fields.Selection([
        ('AM', 'Ampoule'),
        ('BA', 'Barrel'),
        ('BC', 'Bottlecrate'),
        ('BE', 'Bundle'),
        ('BG', 'Bag'),
        ('BJ', 'Bucket'),
        ('BL', 'Bale'),
        ('BQ', 'Bottle protected'),
        ('BR', 'Bar'),
        ('BT', 'Bolt'),
        ('BX', 'Box'),
        ('BZ', 'Bars'),
        ('CA', 'Can'),
        ('CB', 'Cigarette Boxes'),
        ('CG', 'Cage'),
        ('CH', 'Chest'),
        ('CI', 'Canister'),
        ('CL', 'Coil'),
        ('CR', 'Crate'),
        ('CS', 'Case'),
        ('CT', 'Carton'),
        ('CY', 'Cylinder'),
        ('DJ', 'Demijohn'),
        ('DR', 'Drum'),
        ('EN', 'Envelope'),
        ('GB', 'Gas bottle'),
        ('GI', 'Girder'),
        ('GN', 'Grams'),
        ('GT', 'Gross Ton'),
        ('HE', 'Head'),
        ('HR', 'Hamper'),
        ('JG', 'Jug'),
        ('JR', 'Jar'),
        ('JT', 'Jutebag'),
        ('KG', 'Keg'),
        ('KT', 'Kit'),
        ('LF', 'Leaf'),
        ('LG', 'Log'),
        ('LT', 'Lot'),
        ('LZ', 'Liters'),
        ('ML', 'Milliliters'),
        ('MT', 'Mat'),
        ('NE', 'Unpacked'),
        ('NT', 'Net'),
        ('PA', 'Packet'),
        ('PD', 'Pad'),
        ('PG', 'Plate'),
        ('PH', 'Pitcher'),
        ('PI', 'Pipe'),
        ('PK', 'Pack'),
        ('PL', 'Pail'),
        ('PN', 'Plank'),
        ('PO', 'Pouch'),
        ('PP', 'Polybags'),
        ('PT', 'Pot'),
        ('PU', 'Traypack'),
        ('PX', 'Pallet'),
        ('PY', 'Plates'),
        ('RD', 'Rod'),
        ('RG', 'Ring'),
        ('RL', 'Reel'),
        ('RO', 'Roll'),
        ('SA', 'Sack'),
        ('SC', 'Sleeve carton'),
        ('SD', 'Spindle'),
        ('SE', 'Suitcase'),
        ('SH', 'Sachet'),
        ('SK', 'Skid'),
        ('SL', 'Slipsheet'),
        ('SM', 'Sheetmetal'),
        ('SO', 'Spool'),
        ('SS', 'Blocks'),
        ('ST', 'Sheet'),
        ('SU', 'Set'),
        ('SW', 'Shrinkwrapped'),
        ('SX', 'Straw'),
        ('TB', 'Tub'),
        ('TC', 'Tea-chest'),
        ('TD', 'Tube collapsible'),
        ('TK', 'Tank'),
        ('TN', 'Tin'),
        ('TO', 'Tonne'),
        ('TR', 'Trunk'),
        ('TS', 'Truss'),
        ('TU', 'Tube'),
        ('TV', 'Tubes'),
        ('TY', 'Tank cylindrical'),
        ('TZ', 'Bundle tubes'),
        ('VA', 'Vat'),
        ('VG', 'Bulk gas'),
        ('VI', 'Vial'),
        ('VK', 'Vanpack'),
        ('VP', 'Vacuum-packed'),
        ('VQ', 'Bulk liquids'),
        ('VR', 'Bulk solid large'),
        ('VS', 'Bulk scrap metal'),
        ('VY', 'Bulk fine'),
        ('WB', 'Wickerbottle'),
        ('ZZ', 'Mutually defined'),
    ], string='Packaging Unit', default='NT',
       help='eTIMS Packaging Unit Code')

    l10n_ke_qty_unit_code = fields.Selection([
        ('BA', 'Barrel'),
        ('BE', 'Bundle'),
        ('BG', 'Bag'),
        ('BL', 'Block'),
        ('BT', 'Bolt'),
        ('BX', 'Box'),
        ('CA', 'Carat'),
        ('CM', 'Centimeter'),
        ('CR', 'Carat'),
        ('CT', 'Carton'),
        ('DZ', 'Dozen'),
        ('FT', 'Feet'),
        ('G', 'Gram'),
        ('GA', 'Gallon'),
        ('GR', 'Gross'),
        ('GW', 'Gross Weight'),
        ('KG', 'Kilogram'),
        ('KM', 'Kilometer'),
        ('KW', 'Kilowatt'),
        ('L', 'Liter'),
        ('LB', 'Pound'),
        ('M', 'Meter'),
        ('M2', 'Square meter'),
        ('M3', 'Cubic meter'),
        ('MG', 'Milligram'),
        ('ML', 'Milliliter'),
        ('MM', 'Millimeter'),
        ('MT', 'Metric Ton'),
        ('NO', 'Number'),
        ('OZ', 'Ounce'),
        ('PA', 'Packet'),
        ('PC', 'Piece'),
        ('PK', 'Pack'),
        ('PR', 'Pair'),
        ('RL', 'Roll'),
        ('SET', 'Set'),
        ('SQ', 'Square'),
        ('TN', 'Net Ton'),
        ('TU', 'Tube'),
        ('U', 'Unit'),
        ('YD', 'Yard'),
    ], string='Quantity Unit', default='U',
       help='eTIMS Quantity Unit Code')

    # Product Type for eTIMS
    l10n_ke_product_type = fields.Selection([
        ('1', 'Raw Material'),
        ('2', 'Finished Product'),
        ('3', 'Service'),
    ], string='eTIMS Product Type', default='2',
       help='Product type classification for eTIMS')

    # Tax Type
    l10n_ke_tax_type = fields.Selection([
        ('A', 'A - Exempt'),
        ('B', 'B - Standard Rate (16%)'),
        ('C', 'C - Zero Rate (0%)'),
        ('D', 'D - Non-VAT'),
        ('E', 'E - Reduced Rate (8%)'),
    ], string='eTIMS Tax Type', default='B',
       help='Tax type classification for eTIMS')

    # Country of Origin
    l10n_ke_origin_country_id = fields.Many2one(
        'res.country',
        string='Country of Origin',
        default=lambda self: self.env.ref('base.ke', raise_if_not_found=False),
        help='Country of origin for eTIMS reporting',
    )

    # Additional eTIMS fields
    l10n_ke_insurance_applicable = fields.Boolean(
        string='Insurance Applicable',
        default=False,
        help='Whether insurance is applicable for this product',
    )

    def action_register_etims(self):
        """Register product with KRA eTIMS."""
        self.ensure_one()

        if self.l10n_ke_etims_registered:
            raise UserError(_('This product is already registered with eTIMS.'))

        if not self.l10n_ke_item_class_id:
            raise UserError(_('Please select a UNSPSC Classification before registering with eTIMS.'))

        config = self.env['etims.config'].get_config(self.company_id or self.env.company)

        # Prepare item data
        item_data = self._prepare_etims_item_data(config)

        try:
            result = config._call_api('/saveItem', item_data)

            if result.get('resultCd') == '000':
                result_data = result.get('data', {})
                self.write({
                    'l10n_ke_etims_registered': True,
                    'l10n_ke_etims_item_code': result_data.get('itemCd') or self.default_code or str(self.id),
                    'l10n_ke_etims_registration_date': fields.Datetime.now(),
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
                error_msg = result.get('resultMsg', 'Unknown error')
                raise UserError(_('eTIMS Error: %s') % error_msg)

        except UserError:
            raise
        except Exception as e:
            _logger.error('eTIMS item registration error: %s', str(e))
            raise UserError(_('Failed to register with eTIMS: %s') % str(e))

    def _prepare_etims_item_data(self, config):
        """Prepare item data for eTIMS API."""
        self.ensure_one()

        item_code = self.default_code or self.l10n_ke_etims_item_code or str(self.id)

        return {
            'itemCd': item_code[:20],  # Max 20 chars
            'itemClsCd': self.l10n_ke_item_class_id.code if self.l10n_ke_item_class_id else '',
            'itemTyCd': self.l10n_ke_product_type or '2',
            'itemNm': (self.name or '')[:200],
            'itemStdNm': (self.name or '')[:200],
            'orgnNatCd': self.l10n_ke_origin_country_id.code if self.l10n_ke_origin_country_id else 'KE',
            'pkgUnitCd': self.l10n_ke_pkg_unit_code or 'NT',
            'qtyUnitCd': self.l10n_ke_qty_unit_code or 'U',
            'taxTyCd': self.l10n_ke_tax_type or 'B',
            'btchNo': '',
            'bcd': (self.barcode or '')[:20],
            'dftPrc': self.list_price or 0,
            'grpPrcL1': self.list_price or 0,
            'grpPrcL2': self.list_price or 0,
            'grpPrcL3': self.list_price or 0,
            'grpPrcL4': self.list_price or 0,
            'grpPrcL5': self.list_price or 0,
            'addInfo': (self.description_sale or '')[:7] if self.description_sale else '',  # Max 7 chars per spec
            'sftyQty': 0,
            'isrcAplcbYn': 'Y' if self.l10n_ke_insurance_applicable else 'N',
            'useYn': 'Y' if self.active else 'N',
            'regrId': (self.env.user.login or 'admin')[:20],
            'regrNm': (self.env.user.name or 'Admin')[:60],
            'modrId': (self.env.user.login or 'admin')[:20],
            'modrNm': (self.env.user.name or 'Admin')[:60],
        }

    def action_bulk_register_etims(self):
        """Bulk register selected products with eTIMS."""
        products_to_register = self.filtered(lambda p: not p.l10n_ke_etims_registered)

        if not products_to_register:
            raise UserError(_('All selected products are already registered with eTIMS.'))

        # Check all have UNSPSC codes
        missing_unspsc = products_to_register.filtered(lambda p: not p.l10n_ke_item_class_id)
        if missing_unspsc:
            raise UserError(_(
                'The following products are missing UNSPSC classification:\n%s'
            ) % '\n'.join(missing_unspsc.mapped('name')))

        success_count = 0
        failed_products = []

        for product in products_to_register:
            try:
                product.action_register_etims()
                success_count += 1
            except Exception as e:
                _logger.warning('Failed to register product %s: %s', product.name, str(e))
                failed_products.append(f"{product.name}: {str(e)}")

        message = _('Registered: %d') % success_count
        if failed_products:
            message += _('\nFailed: %d') % len(failed_products)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Registration Complete'),
                'message': message,
                'type': 'success' if not failed_products else 'warning',
            }
        }


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_register_etims(self):
        """Register product variant with eTIMS."""
        return self.product_tmpl_id.action_register_etims()

    def _get_etims_item_code(self):
        """Get the eTIMS item code for this product."""
        self.ensure_one()
        return (
            self.product_tmpl_id.l10n_ke_etims_item_code or
            self.default_code or
            str(self.id)
        )

    def _get_etims_item_class_code(self):
        """Get the UNSPSC classification code for this product."""
        self.ensure_one()
        if self.product_tmpl_id.l10n_ke_item_class_id:
            return self.product_tmpl_id.l10n_ke_item_class_id.code
        return ''

    def _get_etims_unit_codes(self):
        """Get packaging and quantity unit codes."""
        self.ensure_one()
        tmpl = self.product_tmpl_id
        return {
            'pkg_unit': tmpl.l10n_ke_pkg_unit_code or 'NT',
            'qty_unit': tmpl.l10n_ke_qty_unit_code or 'U',
        }

    def _get_etims_tax_type(self):
        """Get the eTIMS tax type for this product."""
        self.ensure_one()
        return self.product_tmpl_id.l10n_ke_tax_type or 'B'
