# -*- coding: utf-8 -*-
"""
eTIMS OSCU and UNSPSC Code Management

These models store KRA standard codes fetched from eTIMS including:
- Item Classification (UNSPSC codes)
- Tax Types
- Unit Codes (Packaging and Quantity)
- Payment Types
- Country Codes
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class EtimsCode(models.Model):
    """
    Stores KRA standard codes fetched from eTIMS.
    These codes are used throughout the system for compliance.
    """
    _name = 'etims.code'
    _description = 'eTIMS OSCU Code'
    _rec_name = 'name'
    _order = 'code_type, code'

    code_type = fields.Selection([
        ('01', 'Item Classification (UNSPSC)'),
        ('02', 'Taxation Type'),
        ('03', 'Country'),
        ('04', 'Packaging Unit'),
        ('05', 'Quantity Unit'),
        ('06', 'Payment Type'),
        ('07', 'Transaction Type'),
        ('08', 'Stock Movement Type'),
        ('09', 'Product Type'),
        ('10', 'Import Status'),
        ('11', 'Currency'),
        ('12', 'Refund Reason'),
    ], string='Code Type', required=True, index=True)

    code = fields.Char(string='Code', required=True, index=True)
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_type_uniq', 'unique(code_type, code)',
         'Code must be unique within its type.'),
    ]

    @api.model
    def create_or_update(self, vals):
        """Create or update a code record."""
        existing = self.search([
            ('code_type', '=', vals.get('code_type')),
            ('code', '=', vals.get('code')),
        ], limit=1)

        if existing:
            existing.write(vals)
            return existing
        return self.create(vals)

    @api.model
    def get_code(self, code_type, code):
        """Get a specific code record."""
        return self.search([
            ('code_type', '=', code_type),
            ('code', '=', code),
        ], limit=1)

    @api.model
    def get_codes_by_type(self, code_type):
        """Get all codes of a specific type."""
        return self.search([('code_type', '=', code_type)])


class EtimsItemClass(models.Model):
    """
    eTIMS Item Classification (UNSPSC Codes)

    UNSPSC (United Nations Standard Products and Services Code) is a unique
    classification code required for products sold in Kenya. These codes
    are fetched directly from eTIMS.

    Per KRA requirements, every product must have a valid UNSPSC classification
    before it can be registered and sold.
    """
    _name = 'etims.item.class'
    _description = 'eTIMS Item Classification (UNSPSC)'
    _rec_name = 'display_name'
    _order = 'code'

    code = fields.Char(string='Classification Code', required=True, index=True,
                       help='UNSPSC Classification Code from KRA')
    name = fields.Char(string='Name', required=True)
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)

    # Tax information associated with this classification
    tax_type_code = fields.Char(string='Tax Type Code',
                                help='Default tax type for this classification (A, B, C, D, E)')
    tax_rate = fields.Float(string='Tax Rate (%)', help='Tax rate percentage')

    # Hierarchy - UNSPSC codes have a hierarchical structure
    parent_code = fields.Char(string='Parent Code')
    level = fields.Integer(string='Level', help='Hierarchy level (1=Segment, 2=Family, 3=Class, 4=Commodity)')

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Classification code must be unique.'),
    ]

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.code}] {rec.name}" if rec.code and rec.name else rec.name or rec.code

    @api.model
    def search_by_name_or_code(self, search_term, limit=100):
        """Search classifications by name or code."""
        return self.search([
            '|',
            ('code', 'ilike', search_term),
            ('name', 'ilike', search_term),
        ], limit=limit)


class EtimsCodeSync(models.Model):
    """
    Handles synchronization of OSCU codes from KRA eTIMS.
    This is typically triggered by a scheduled action.
    """
    _name = 'etims.code.sync'
    _description = 'eTIMS Code Sync Log'

    sync_date = fields.Datetime(string='Sync Date', default=fields.Datetime.now, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    code_type = fields.Char(string='Code Type Synced')
    records_synced = fields.Integer(string='Records Synced', default=0)
    status = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('partial', 'Partial'),
    ], string='Status', default='success')
    error_message = fields.Text(string='Error Message')

    @api.model
    def sync_all_codes(self, company=None):
        """
        Fetch all standard codes from KRA eTIMS.
        This is called by the scheduled action.
        """
        company = company or self.env.company
        config = self.env['etims.config'].get_config(company)

        # Code types to fetch
        code_endpoints = [
            ('/selectCodeList', '01', 'Item Classification'),
            ('/selectCodeList', '02', 'Taxation Type'),
            ('/selectCodeList', '04', 'Packaging Unit'),
            ('/selectCodeList', '05', 'Quantity Unit'),
            ('/selectCodeList', '06', 'Payment Type'),
        ]

        total_synced = 0
        errors = []

        for endpoint, code_type, type_name in code_endpoints:
            try:
                result = config._call_api(endpoint, {'cdClsCd': code_type})

                if result.get('resultCd') == '000':
                    data_list = result.get('data', {}).get('clsList', [])
                    count = self._process_code_list(code_type, data_list)
                    total_synced += count
                    _logger.info('Synced %d %s codes', count, type_name)
                else:
                    errors.append(f"{type_name}: {result.get('resultMsg', 'Unknown error')}")

            except Exception as e:
                errors.append(f"{type_name}: {str(e)}")
                _logger.error('Error syncing %s: %s', type_name, str(e))

        # Sync item classifications separately (larger dataset)
        try:
            cls_count = self._sync_item_classifications(config)
            total_synced += cls_count
        except Exception as e:
            errors.append(f"Item Classifications: {str(e)}")

        # Log the sync
        self.create({
            'company_id': company.id,
            'code_type': 'all',
            'records_synced': total_synced,
            'status': 'failed' if errors and total_synced == 0 else ('partial' if errors else 'success'),
            'error_message': '\n'.join(errors) if errors else False,
        })

        return total_synced

    def _process_code_list(self, code_type, data_list):
        """Process a list of codes from eTIMS API response."""
        Code = self.env['etims.code']
        count = 0

        for item in data_list:
            Code.create_or_update({
                'code_type': code_type,
                'code': item.get('cd') or item.get('cdCls'),
                'name': item.get('cdNm') or item.get('cdClsNm', ''),
                'description': item.get('cdDesc', ''),
            })
            count += 1

        return count

    def _sync_item_classifications(self, config):
        """Sync item classifications (UNSPSC codes) from eTIMS."""
        ItemClass = self.env['etims.item.class']

        result = config._call_api('/selectItemClsList', {'lastReqDt': '20200101000000'})

        if result.get('resultCd') != '000':
            raise UserError(_('Failed to fetch item classifications: %s') % result.get('resultMsg'))

        data_list = result.get('data', {}).get('itemClsList', [])
        count = 0

        for item in data_list:
            code = item.get('itemClsCd', '')
            if not code:
                continue

            existing = ItemClass.search([('code', '=', code)], limit=1)
            vals = {
                'code': code,
                'name': item.get('itemClsNm', ''),
                'tax_type_code': item.get('taxTyCd', ''),
                'tax_rate': float(item.get('taxRate', 0) or 0),
            }

            if existing:
                existing.write(vals)
            else:
                ItemClass.create(vals)

            count += 1

        _logger.info('Synced %d item classifications', count)
        return count

    @api.model
    def action_sync_codes(self):
        """Action button to manually trigger code sync."""
        count = self.sync_all_codes()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Code Sync Complete'),
                'message': _('Synced %d codes from eTIMS.') % count,
                'type': 'success',
            }
        }
