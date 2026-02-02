# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    etims_reported = fields.Boolean(
        string='Reported to eTIMS',
        default=False,
        copy=False,
    )
    etims_move_type = fields.Selection([
        ('01', 'Import'),
        ('02', 'Purchase'),
        ('03', 'Return'),
        ('04', 'Stock Movement'),
        ('05', 'Processing'),
        ('06', 'Adjustment'),
    ], string='eTIMS Move Type')

    etims_report_date = fields.Datetime(
        string='eTIMS Report Date',
        copy=False,
        readonly=True,
    )

    def action_report_to_etims(self):
        """Report stock movement to eTIMS."""
        for move in self:
            if move.etims_reported:
                continue

            if move.state != 'done':
                continue

            config = self.env['etims.config'].get_active_config()
            if not config:
                raise UserError(_('eTIMS is not configured.'))

            api = self.env['etims.api']

            # Determine move type
            move_type = move._determine_etims_move_type()

            # Prepare stock data
            stock_data = move._prepare_etims_stock_data(config, move_type)

            try:
                response = api.save_stock_move(config, stock_data)

                if response.get('resultCd') == '000':
                    move.write({
                        'etims_reported': True,
                        'etims_move_type': move_type,
                        'etims_report_date': fields.Datetime.now(),
                    })
                else:
                    error_msg = response.get('resultMsg', 'Unknown error')
                    _logger.warning('eTIMS stock report failed: %s', error_msg)

            except Exception as e:
                _logger.error('eTIMS stock report error: %s', str(e))

    def _determine_etims_move_type(self):
        """Determine the eTIMS stock movement type."""
        self.ensure_one()

        picking = self.picking_id
        if not picking:
            return '06'  # Adjustment

        # Check picking type
        if picking.picking_type_code == 'incoming':
            if picking.purchase_id:
                return '02'  # Purchase
            return '04'  # Stock Movement

        elif picking.picking_type_code == 'outgoing':
            return '04'  # Stock Movement / Sale

        elif picking.picking_type_code == 'internal':
            return '04'  # Internal transfer

        return '06'  # Default to adjustment

    def _prepare_etims_stock_data(self, config, move_type):
        """Prepare stock movement data for eTIMS."""
        self.ensure_one()

        product = self.product_id

        return {
            'tin': config.tin,
            'bhfId': config.branch_id or '00',
            'sarNo': 1,  # Sequence
            'orgSarNo': 0,
            'regTyCd': move_type,
            'custTin': '',
            'custNm': '',
            'custBhfId': '00',
            'sarTyCd': move_type,
            'ocrnDt': self.date.strftime('%Y%m%d') if self.date else '',
            'totItemCnt': 1,
            'totTaxblAmt': 0,
            'totTaxAmt': 0,
            'totAmt': 0,
            'remark': self.name or '',
            'itemList': [{
                'itemSeq': 1,
                'itemCd': product.default_code or str(product.id),
                'itemClsCd': product.etims_item_class_id.code if product.etims_item_class_id else '',
                'itemNm': product.name,
                'bcd': product.barcode or '',
                'pkgUnitCd': product.etims_pkg_unit_code or 'NT',
                'pkg': self.product_uom_qty,
                'qtyUnitCd': product.etims_qty_unit_code or 'U',
                'qty': self.product_uom_qty,
                'itemExprDt': '',
                'prc': 0,
                'splyAmt': 0,
                'totDcAmt': 0,
                'taxblAmt': 0,
                'taxTyCd': product.etims_tax_type or 'B',
                'taxAmt': 0,
                'totAmt': 0,
            }],
        }


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    etims_reported = fields.Boolean(
        string='Reported to eTIMS',
        compute='_compute_etims_reported',
        store=True,
    )

    @api.depends('move_ids.etims_reported')
    def _compute_etims_reported(self):
        for picking in self:
            picking.etims_reported = all(
                m.etims_reported for m in picking.move_ids if m.state == 'done'
            )

    def action_report_stock_to_etims(self):
        """Report all moves in picking to eTIMS."""
        for picking in self:
            for move in picking.move_ids.filtered(lambda m: m.state == 'done' and not m.etims_reported):
                move.action_report_to_etims()

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
        """Report current inventory to eTIMS."""
        config = self.env['etims.config'].get_active_config()
        if not config:
            raise UserError(_('eTIMS is not configured.'))

        api = self.env['etims.api']

        for quant in self:
            if quant.quantity <= 0:
                continue

            product = quant.product_id

            stock_data = {
                'tin': config.tin,
                'bhfId': config.branch_id or '00',
                'itemCd': product.default_code or str(product.id),
                'rsdQty': quant.quantity,
            }

            try:
                response = api.save_stock_master(config, stock_data)
                if response.get('resultCd') != '000':
                    _logger.warning('eTIMS inventory report failed for %s', product.name)
            except Exception as e:
                _logger.error('eTIMS inventory error: %s', str(e))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('eTIMS Inventory'),
                'message': _('Inventory reported to eTIMS.'),
                'type': 'success',
            }
        }
