# -*- coding: utf-8 -*-

import json
import logging
import requests
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class KRAeTIMSAPI(models.AbstractModel):
    """API Client for KRA e-TIMS OSCU Integration"""
    _name = 'kra.etims.api'
    _description = 'KRA e-TIMS API Client'

    @api.model
    def _get_api_config(self):
        """Get API configuration from company settings"""
        company = self.env.company
        if not company.kra_etims_enabled:
            raise UserError(_('KRA e-TIMS is not enabled for this company.'))
        
        config = {
            'base_url': company.kra_etims_base_url or 'https://etims-sbx.kra.go.ke/etims-api',
            'tin': company.kra_etims_tin,
            'bhf_id': company.kra_etims_bhf_id,
            'device_serial': company.kra_etims_device_serial,
            'cmc_key': company.kra_etims_cmc_key,
            'timeout': 30,
        }
        
        if not all([config['tin'], config['bhf_id'], config['cmc_key']]):
            raise UserError(_('Please configure KRA e-TIMS settings (TIN, Branch ID, and CMC Key are required).'))
        
        return config

    @api.model
    def _make_request(self, endpoint, data):
        """Make HTTP request to e-TIMS API"""
        config = self._get_api_config()
        url = f"{config['base_url']}/{endpoint}"
        
        # Add common headers including CMC Key for authentication
        headers = {
            'Content-Type': 'application/json',
            'tin': config['tin'],
            'bhfId': config['bhf_id'],
            'cmcKey': config['cmc_key'],  # Communication Key for authentication
        }
        
        # Add timestamp
        data['reqDt'] = datetime.now().strftime('%Y%m%d%H%M%S')
        
        _logger.info(f"KRA e-TIMS Request to {endpoint}: {json.dumps(data, indent=2)}")
        
        try:
            response = requests.post(
                url,
                json=data,
                headers=headers,
                timeout=config['timeout']
            )
            response.raise_for_status()
            
            result = response.json()
            _logger.info(f"KRA e-TIMS Response: {json.dumps(result, indent=2)}")
            
            # Check for API-level errors
            if result.get('resultCd') != '000':
                error_msg = result.get('resultMsg', 'Unknown error')
                raise UserError(_(f'KRA e-TIMS Error: {error_msg}'))
            
            return result
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"KRA e-TIMS API Error: {str(e)}")
            raise UserError(_(f'Failed to connect to KRA e-TIMS: {str(e)}'))

    # ==================== Device Management ====================
    
    @api.model
    def initialize_device(self, device_serial, tin, bhf_id):
        """Initialize device with e-TIMS"""
        data = {
            'tin': tin,
            'bhfId': bhf_id,
            'dvcSrlNo': device_serial,
        }
        return self._make_request('initializer/selectInitInfo', data)

    @api.model
    def select_codes(self, code_type, last_request_date=None):
        """Retrieve code information from e-TIMS"""
        data = {
            'tin': self.env.company.kra_etims_tin,
            'bhfId': self.env.company.kra_etims_bhf_id,
            'lastReqDt': last_request_date or '20200101000000',
            'cdCls': code_type,  # 01: Item Class, 02: Country, etc.
        }
        return self._make_request('code/selectCodes', data)

    # ==================== Item/Product Management ====================
    
    @api.model
    def save_item(self, product):
        """Register or update item in e-TIMS"""
        data = {
            'tin': self.env.company.kra_etims_tin,
            'bhfId': self.env.company.kra_etims_bhf_id,
            'itemCd': product.default_code or product.id,
            'itemClsCd': product.kra_item_class_code or '5020230500',
            'itemTyCd': product.kra_item_type_code or '2',  # 1: Raw Material, 2: Finished Product, 3: Service
            'itemNm': product.name[:200],
            'itemStdNm': product.name[:200],
            'orgnNatCd': product.kra_origin_country_code or 'KE',
            'pkgUnitCd': product.kra_package_unit_code or 'NT',  # NT: Not Applicable
            'qtyUnitCd': product.uom_id.kra_unit_code or 'U',
            'taxTyCd': product.kra_tax_type_code or 'B',  # B: VAT 16%
            'btchNo': None,
            'bcd': None,
            'dftPrc': product.list_price,
            'addInfo': product.description_sale or '',
            'sftyQty': 0,
            'isrcAplcbYn': 'N',  # Insurance applicable
            'useYn': 'Y' if product.active else 'N',
            'regrNm': self.env.user.name,
            'regrId': str(self.env.user.id),
            'modrNm': self.env.user.name,
            'modrId': str(self.env.user.id),
        }
        return self._make_request('items/saveItem', data)

    # ==================== Invoice Management ====================
    
    @api.model
    def save_sales_invoice(self, invoice):
        """Submit sales invoice to e-TIMS"""
        if invoice.move_type not in ['out_invoice', 'out_refund']:
            raise UserError(_('Only customer invoices and credit notes can be submitted to e-TIMS.'))
        
        # Determine invoice type
        if invoice.move_type == 'out_refund':
            sales_ty_cd = '02'  # Credit Note
            orgn_invc_no = invoice.reversed_entry_id.kra_invoice_no or 0
        else:
            sales_ty_cd = '01'  # Normal Sale
            orgn_invc_no = 0
        
        # Build item list
        item_list = []
        for idx, line in enumerate(invoice.invoice_line_ids.filtered(lambda l: not l.display_type), start=1):
            tax_rate = 0
            tax_type_cd = 'B'  # Default to VAT 16%
            
            if line.tax_ids:
                tax = line.tax_ids[0]
                tax_rate = tax.amount
                if hasattr(tax, 'kra_tax_type_code'):
                    tax_type_cd = tax.kra_tax_type_code
            
            # Calculate amounts
            item_expr_dt = None
            if line.product_id.kra_item_type_code == '1':  # Raw material
                item_expr_dt = None  # Can be set based on expiry date if available
            
            discount_amt = line.quantity * line.price_unit * (line.discount / 100.0)
            taxable_amt = line.price_subtotal
            tax_amt = line.price_total - line.price_subtotal
            total_amt = line.price_total
            
            item_list.append({
                'itemSeq': idx,
                'itemCd': line.product_id.default_code or str(line.product_id.id),
                'itemClsCd': line.product_id.kra_item_class_code or '5020230500',
                'itemNm': line.name[:200],
                'bcd': None,
                'pkgUnitCd': line.product_id.kra_package_unit_code or 'NT',
                'pkg': line.quantity,
                'qtyUnitCd': line.product_uom_id.kra_unit_code or 'U',
                'qty': line.quantity,
                'prc': line.price_unit,
                'splyAmt': line.price_subtotal,
                'dcRt': line.discount,
                'dcAmt': discount_amt,
                'isrccCd': None,
                'isrccNm': None,
                'isrcRt': 0,
                'isrcAmt': 0,
                'taxTyCd': tax_type_cd,
                'taxblAmt': taxable_amt,
                'taxTyCdNm': tax.name if line.tax_ids else 'VAT',
                'taxRt': tax_rate,
                'taxAmt': tax_amt,
                'totAmt': total_amt,
                'itemExprDt': item_expr_dt,
            })
        
        # Payment type - default to cash
        pmt_ty_cd = invoice.kra_payment_type or '01'  # 01: Cash, 02: Credit, 03: Card, etc.
        
        # Build main invoice data
        data = {
            'tin': self.env.company.kra_etims_tin,
            'bhfId': self.env.company.kra_etims_bhf_id,
            'invcNo': invoice.kra_invoice_counter or 1,
            'orgInvcNo': orgn_invc_no,
            'custTin': invoice.partner_id.vat or None,
            'custNm': invoice.partner_id.name[:60],
            'salesTyCd': sales_ty_cd,
            'rcptTyCd': 'S',  # S: Sale, P: Purchase, R: Refund, etc.
            'pmtTyCd': pmt_ty_cd,
            'salesSttsCd': '02',  # 01: Confirmed, 02: Completed
            'cfmDt': invoice.invoice_date.strftime('%Y%m%d%H%M%S') if invoice.invoice_date else None,
            'salesDt': invoice.invoice_date.strftime('%Y%m%d') if invoice.invoice_date else fields.Date.today().strftime('%Y%m%d'),
            'stockRlsDt': invoice.invoice_date.strftime('%Y%m%d') if invoice.invoice_date else None,
            'cnclReqDt': None,
            'cnclDt': None,
            'rfdDt': None,
            'rfdRsnCd': None,
            'totItemCnt': len(item_list),
            'taxblAmtA': sum(item['taxblAmt'] for item in item_list if item['taxTyCd'] == 'A'),
            'taxblAmtB': sum(item['taxblAmt'] for item in item_list if item['taxTyCd'] == 'B'),
            'taxblAmtC': sum(item['taxblAmt'] for item in item_list if item['taxTyCd'] == 'C'),
            'taxblAmtD': sum(item['taxblAmt'] for item in item_list if item['taxTyCd'] == 'D'),
            'taxRtA': 0,
            'taxRtB': 16,
            'taxRtC': 8,
            'taxRtD': 0,
            'taxAmtA': sum(item['taxAmt'] for item in item_list if item['taxTyCd'] == 'A'),
            'taxAmtB': sum(item['taxAmt'] for item in item_list if item['taxTyCd'] == 'B'),
            'taxAmtC': sum(item['taxAmt'] for item in item_list if item['taxTyCd'] == 'C'),
            'taxAmtD': sum(item['taxAmt'] for item in item_list if item['taxTyCd'] == 'D'),
            'totTaxblAmt': invoice.amount_untaxed,
            'totTaxAmt': invoice.amount_tax,
            'totAmt': invoice.amount_total,
            'prchrAcptcYn': 'N',
            'remark': invoice.narration or '',
            'regrId': str(self.env.user.id),
            'regrNm': self.env.user.name,
            'modrNm': self.env.user.name,
            'modrId': str(self.env.user.id),
            'receipt': {
                'custTin': invoice.partner_id.vat or None,
                'custMblNo': invoice.partner_id.mobile or invoice.partner_id.phone or None,
                'rptNo': 0,
            },
            'itemList': item_list,
        }
        
        result = self._make_request('trnsSales/saveSales', data)
        
        # Update invoice with e-TIMS data
        if result.get('resultCd') == '000':
            data_from_api = result.get('data', {})
            invoice.write({
                'kra_invoice_no': data.get('invcNo'),
                'kra_internal_data': data_from_api.get('intrlData'),
                'kra_receipt_signature': data_from_api.get('rcptSign'),
                'kra_sdc_datetime': data_from_api.get('sdcDateTime'),
                'kra_submission_date': fields.Datetime.now(),
                'kra_submission_status': 'submitted',
                'kra_cu_serial': data_from_api.get('custSrlNo'),
            })
        
        return result

    @api.model
    def select_invoice(self, invoice_no):
        """Retrieve invoice details from e-TIMS"""
        data = {
            'tin': self.env.company.kra_etims_tin,
            'bhfId': self.env.company.kra_etims_bhf_id,
            'invcNo': invoice_no,
        }
        return self._make_request('trnsSales/selectInvoice', data)

    # ==================== Stock Management ====================
    
    @api.model
    def save_stock_movement(self, product, qty, movement_type, reference):
        """Report stock movement to e-TIMS"""
        data = {
            'tin': self.env.company.kra_etims_tin,
            'bhfId': self.env.company.kra_etims_bhf_id,
            'sarNo': reference,
            'orgSarNo': 0,
            'regTyCd': movement_type,  # 'P': Purchase, 'S': Sale, 'A': Adjustment
            'custTin': None,
            'custNm': None,
            'custBhfId': None,
            'sarTyCd': '11',  # 11: Goods
            'ocrnDt': fields.Datetime.now().strftime('%Y%m%d'),
            'totItemCnt': 1,
            'totTaxblAmt': 0,
            'totTaxAmt': 0,
            'totAmt': 0,
            'remark': reference,
            'regrId': str(self.env.user.id),
            'regrNm': self.env.user.name,
            'modrNm': self.env.user.name,
            'modrId': str(self.env.user.id),
            'itemList': [{
                'itemSeq': 1,
                'itemCd': product.default_code or str(product.id),
                'itemClsCd': product.kra_item_class_code or '5020230500',
                'itemNm': product.name[:200],
                'bcd': None,
                'pkgUnitCd': product.kra_package_unit_code or 'NT',
                'pkg': qty,
                'qtyUnitCd': product.uom_id.kra_unit_code or 'U',
                'qty': qty,
                'itemExprDt': None,
                'prc': product.standard_price,
                'splyAmt': product.standard_price * qty,
                'totDcAmt': 0,
                'taxblAmt': product.standard_price * qty,
                'taxTyCd': product.kra_tax_type_code or 'B',
                'taxAmt': 0,
                'totAmt': product.standard_price * qty,
            }],
        }
        return self._make_request('stock/saveStockMaster', data)
