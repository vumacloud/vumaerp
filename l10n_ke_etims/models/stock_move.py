# -*- coding: utf-8 -*-
"""
Stock Movement eTIMS Integration

Per KRA requirements, stock movements must be reported to eTIMS.
This includes:
- Incoming stock (purchases, imports)
- Outgoing stock (sales, transfers)
- Internal transfers
- Inventory adjustments

Stock moves auto-send to eTIMS post-validation for registered products.
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    # eTIMS Fields
    l10n_ke_etims_reported = fields.Boolean(
        string='Reported to eTIMS',
        default=False,
        copy=False,
        help='Indicates if this stock move has been reported to KRA eTIMS',
    )
    l10n_ke_etims_move_type = fields.Selection([
        ('01', 'Import'),
        ('02', 'Purchase'),
        ('03', 'Return'),
        ('04', 'Stock Movement'),
        ('05', 'Processing'),
        ('06', 'Adjustment'),
    ], string='eTIMS Move Type', copy=False)

    l10n_ke_etims_report_date = fields.Datetime(
        string='eTIMS Report Date',
        copy=False,
        readonly=True,
    )
    l10n_ke_etims_response = fields.Text(
        string='eTIMS Response',
        copy=False,
        readonly=True,
    )

    def _action_done(self, cancel_backorder=False):
        """Override to auto-report to eTIMS after validation."""
        res = super()._action_done(cancel_backorder=cancel_backorder)

        # Auto-report to eTIMS for Kenyan companies
        for move in self:
            if (move.company_id.country_id.code == 'KE' and
                    move.product_id.product_tmpl_id.l10n_ke_etims_registered and
                    not move.l10n_ke_etims_reported):
                try:
                    move._report_to_etims()
                except Exception as e:
                    # Log but don't block the stock move
                    _logger.warning('eTIMS stock report failed for move %s: %s', move.id, str(e))

        return res

    def _report_to_etims(self):
        """Report stock movement to eTIMS."""
        self.ensure_one()

        if self.l10n_ke_etims_reported:
            return

        if self.state != 'done':
            return

        # Check if product is registered
        if not self.product_id.product_tmpl_id.l10n_ke_etims_registered:
            _logger.info('Skipping eTIMS report for unregistered product: %s', self.product_id.name)
            return

        try:
            config = self.env['etims.config'].get_config(self.company_id)
        except UserError:
            _logger.info('eTIMS not configured for company %s, skipping stock report', self.company_id.name)
            return

        # Determine move type
        move_type = self._determine_etims_move_type()

        # Prepare stock data
        stock_data = self._prepare_etims_stock_data(config, move_type)

        try:
            result = config._call_api('/saveStockMaster', stock_data)

            if result.get('resultCd') == '000':
                self.write({
                    'l10n_ke_etims_reported': True,
                    'l10n_ke_etims_move_type': move_type,
                    'l10n_ke_etims_report_date': fields.Datetime.now(),
                    'l10n_ke_etims_response': str(result),
                })
                _logger.info('Stock move %s reported to eTIMS', self.id)
            else:
                error_msg = result.get('resultMsg', 'Unknown error')
                _logger.warning('eTIMS stock report failed: %s', error_msg)
                self.l10n_ke_etims_response = str(result)

        except Exception as e:
            _logger.error('eTIMS stock report error: %s', str(e))
            self.l10n_ke_etims_response = str(e)

    def _determine_etims_move_type(self):
        """Determine the eTIMS stock movement type based on picking type."""
        self.ensure_one()

        picking = self.picking_id
        if not picking:
            return '06'  # Adjustment

        # Check picking type
        if picking.picking_type_code == 'incoming':
            # Check if it's a purchase or return
            if picking.purchase_id:
                return '02'  # Purchase
            # Check for incoming from supplier
            if picking.partner_id and picking.partner_id.supplier_rank > 0:
                return '02'  # Purchase
            return '03'  # Return (e.g., customer return)

        elif picking.picking_type_code == 'outgoing':
            # Check if it's a sale or return
            if hasattr(picking, 'sale_id') and picking.sale_id:
                return '04'  # Stock Movement (Sale)
            return '04'  # Stock Movement

        elif picking.picking_type_code == 'internal':
            return '04'  # Internal transfer

        return '06'  # Default to adjustment

    def _prepare_etims_stock_data(self, config, move_type):
        """Prepare stock movement data for eTIMS API."""
        self.ensure_one()

        product = self.product_id
        tmpl = product.product_tmpl_id

        # Get date in eTIMS format
        move_date = self.date.strftime('%Y%m%d') if self.date else fields.Date.today().strftime('%Y%m%d')

        # Calculate amounts if available
        unit_price = 0
        if self.sale_line_id:
            unit_price = self.sale_line_id.price_unit
        elif self.purchase_line_id:
            unit_price = self.purchase_line_id.price_unit
        else:
            unit_price = product.list_price or 0

        supply_amount = unit_price * self.product_uom_qty

        return {
            'sarNo': self.id,  # Stock Adjustment/Receipt Number
            'orgSarNo': 0,  # Original SAR number for adjustments
            'regTyCd': move_type,  # Registration Type Code
            'custTin': self.picking_id.partner_id.vat if self.picking_id and self.picking_id.partner_id else '',
            'custNm': (self.picking_id.partner_id.name if self.picking_id and self.picking_id.partner_id else '')[:100],
            'custBhfId': '00',
            'sarTyCd': move_type,  # Stock Adjustment/Receipt Type Code
            'ocrnDt': move_date,  # Occurrence Date
            'totItemCnt': 1,
            'totTaxblAmt': round(supply_amount, 2),
            'totTaxAmt': 0,  # Will be calculated if needed
            'totAmt': round(supply_amount, 2),
            'remark': (self.name or '')[:400],
            'regrId': (self.env.user.login or 'admin')[:20],
            'regrNm': (self.env.user.name or 'Admin')[:60],
            'modrId': (self.env.user.login or 'admin')[:20],
            'modrNm': (self.env.user.name or 'Admin')[:60],
            'itemList': [{
                'itemSeq': 1,
                'itemCd': product._get_etims_item_code()[:20],
                'itemClsCd': product._get_etims_item_class_code(),
                'itemNm': (product.name or '')[:200],
                'bcd': (product.barcode or '')[:20],
                'pkgUnitCd': product._get_etims_unit_codes()['pkg_unit'],
                'pkg': self.product_uom_qty,
                'qtyUnitCd': product._get_etims_unit_codes()['qty_unit'],
                'qty': self.product_uom_qty,
                'itemExprDt': '',  # Expiry date if applicable
                'prc': round(unit_price, 2),
                'splyAmt': round(supply_amount, 2),
                'totDcAmt': 0,
                'taxblAmt': round(supply_amount, 2),
                'taxTyCd': product._get_etims_tax_type(),
                'taxAmt': 0,
                'totAmt': round(supply_amount, 2),
            }],
        }

    def action_report_to_etims(self):
        """Manual action to report stock movement to eTIMS."""
        for move in self:
            if move.l10n_ke_etims_reported:
                continue

            if move.state != 'done':
                raise UserError(_('Only completed stock moves can be reported to eTIMS.'))

            if not move.product_id.product_tmpl_id.l10n_ke_etims_registered:
                raise UserError(_(
                    'Product "%s" must be registered with eTIMS before reporting stock movements.'
                ) % move.product_id.name)

            move._report_to_etims()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('eTIMS Report'),
                'message': _('Stock movements reported to eTIMS.'),
                'type': 'success',
            }
        }


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    l10n_ke_etims_reported = fields.Boolean(
        string='Reported to eTIMS',
        compute='_compute_etims_reported',
        store=True,
        help='All stock moves in this transfer have been reported to eTIMS',
    )

    @api.depends('move_ids.l10n_ke_etims_reported')
    def _compute_etims_reported(self):
        for picking in self:
            done_moves = picking.move_ids.filtered(lambda m: m.state == 'done')
            if done_moves:
                picking.l10n_ke_etims_reported = all(m.l10n_ke_etims_reported for m in done_moves)
            else:
                picking.l10n_ke_etims_reported = False

    def action_report_stock_to_etims(self):
        """Report all moves in picking to eTIMS."""
        for picking in self:
            moves_to_report = picking.move_ids.filtered(
                lambda m: m.state == 'done' and
                          not m.l10n_ke_etims_reported and
                          m.product_id.product_tmpl_id.l10n_ke_etims_registered
            )

            for move in moves_to_report:
                try:
                    move._report_to_etims()
                except Exception as e:
                    _logger.warning('Failed to report move %s: %s', move.id, str(e))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('eTIMS Report'),
                'message': _('Stock movements reported to eTIMS.'),
                'type': 'success',
            }
        }


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def action_report_inventory_to_etims(self):
        """Report current inventory levels to eTIMS."""
        try:
            config = self.env['etims.config'].get_config()
        except UserError as e:
            raise UserError(_('eTIMS not configured: %s') % str(e))

        success_count = 0
        failed_count = 0

        for quant in self.filtered(lambda q: q.quantity > 0):
            product = quant.product_id

            # Skip unregistered products
            if not product.product_tmpl_id.l10n_ke_etims_registered:
                continue

            stock_data = {
                'itemCd': product._get_etims_item_code()[:20],
                'rsdQty': quant.quantity,
            }

            try:
                result = config._call_api('/updateStockMaster', stock_data)
                if result.get('resultCd') == '000':
                    success_count += 1
                else:
                    failed_count += 1
                    _logger.warning('eTIMS inventory report failed for %s: %s',
                                    product.name, result.get('resultMsg'))
            except Exception as e:
                failed_count += 1
                _logger.error('eTIMS inventory error for %s: %s', product.name, str(e))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('eTIMS Inventory'),
                'message': _('Reported: %d, Failed: %d') % (success_count, failed_count),
                'type': 'success' if failed_count == 0 else 'warning',
            }
        }
