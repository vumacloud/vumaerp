# -*- coding: utf-8 -*-
import json
import logging
import requests
from datetime import datetime
from odoo import api, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class EtimsAPI(models.AbstractModel):
    _name = 'etims.api'
    _description = 'eTIMS API Service'

    # API Endpoints
    ENDPOINTS = {
        'device_verification': '/api/device/verification',
        'device_initialization': '/api/device/initialization',
        'code_search': '/api/code/search',
        'customer_search': '/api/customer/search',
        'notice_search': '/api/notice/search',
        'item_cls_search': '/api/itemClass/search',
        'item_save': '/api/item/save',
        'item_search': '/api/item/search',
        'branch_search': '/api/branch/search',
        'branch_customer_save': '/api/branchCustomer/save',
        'branch_user_save': '/api/branchUser/save',
        'branch_insurance_save': '/api/branchInsurance/save',
        'import_item_search': '/api/importItem/search',
        'import_item_update': '/api/importItem/update',
        'sales_save': '/api/trnsSales/saveSales',
        'purchase_sales_search': '/api/trnsPurchase/searchSales',
        'purchase_save': '/api/trnsPurchase/save',
        'stock_move': '/api/stock/move',
        'stock_io_save': '/api/stock/saveIO',
        'stock_master_save': '/api/stock/saveMaster',
        'item_composition_save': '/api/itemComposition/save',
    }

    def _get_headers(self, config):
        """Get API request headers."""
        return {
            'Content-Type': 'application/json',
            'tin': config.tin,
            'bhfId': config.branch_id or '00',
            'cmcKey': config.comm_key or '',
        }

    def _make_request(self, config, endpoint, data=None, method='POST'):
        """Make API request to eTIMS."""
        url = f"{config.get_api_url()}{endpoint}"
        headers = self._get_headers(config)

        _logger.info(f"eTIMS API Request: {method} {url}")
        _logger.debug(f"Request data: {json.dumps(data, indent=2)}")

        try:
            if method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                response = requests.get(url, params=data, headers=headers, timeout=30)

            response.raise_for_status()
            result = response.json()

            _logger.info(f"eTIMS API Response: {result.get('resultCd')} - {result.get('resultMsg')}")
            return result

        except requests.exceptions.Timeout:
            _logger.error("eTIMS API timeout")
            raise UserError(_("eTIMS API request timed out. Please try again."))
        except requests.exceptions.RequestException as e:
            _logger.error(f"eTIMS API error: {str(e)}")
            raise UserError(_("eTIMS API error: %s") % str(e))

    # ==================== Device Management ====================

    def device_verification(self, config, data=None):
        """Verify device with KRA (DeviceVerificationReq)."""
        if data is None:
            data = {
                'tin': config.tin,
                'bhfId': config.branch_id or '00',
                'dvcSrlNo': config.device_serial,
            }
        return self._make_request(config, '/api/device/verification', data)

    def device_initialization(self, config, data=None):
        """Initialize device and get communication key (DeviceInitializationReq)."""
        if data is None:
            data = {
                'tin': config.tin,
                'bhfId': config.branch_id or '00',
                'dvcSrlNo': config.device_serial,
            }
        return self._make_request(config, '/api/device/initialization', data)

    # ==================== Code Management ====================

    def code_search(self, config, code_type, last_req_dt=None):
        """Search code table (CodeSearchReq)."""
        data = {
            'lastReqDt': last_req_dt or '20200101000000',
            'cdType': code_type,
        }
        return self._make_request(config, self.ENDPOINTS['code_search'], data)

    # ==================== Customer Management ====================

    def customer_search(self, config, customer_pin):
        """Search customer by PIN (CustSearchReq)."""
        data = {
            'custmTin': customer_pin,
        }
        return self._make_request(config, self.ENDPOINTS['customer_search'], data)

    def search_customer(self, config, data):
        """Search customer by data dict (alias for customer_search)."""
        return self._make_request(config, self.ENDPOINTS['customer_search'], data)

    # ==================== Item Management ====================

    def item_class_search(self, config, last_req_dt=None):
        """Search item classification codes (ItemClsSearchReq)."""
        data = {
            'lastReqDt': last_req_dt or '20200101000000',
        }
        return self._make_request(config, self.ENDPOINTS['item_cls_search'], data)

    def item_save(self, config, item_data):
        """Register/update item (ItemSaveReq)."""
        return self._make_request(config, self.ENDPOINTS['item_save'], item_data)

    def item_search(self, config, last_req_dt=None):
        """Search registered items (ItemSearchReq)."""
        data = {
            'lastReqDt': last_req_dt or '20200101000000',
        }
        return self._make_request(config, self.ENDPOINTS['item_search'], data)

    # ==================== Branch Management ====================

    def branch_search(self, config, last_req_dt=None):
        """Search branch information (BhfSearchReq)."""
        data = {
            'lastReqDt': last_req_dt or '20200101000000',
        }
        return self._make_request(config, self.ENDPOINTS['branch_search'], data)

    def branch_customer_save(self, config, customer_data):
        """Register branch customer (BhfCustSaveReq)."""
        return self._make_request(config, self.ENDPOINTS['branch_customer_save'], customer_data)

    def branch_user_save(self, config, user_data):
        """Register branch user (BhfUserSaveReq)."""
        return self._make_request(config, self.ENDPOINTS['branch_user_save'], user_data)

    # ==================== Sales Transaction ====================

    def sales_save(self, config, invoice_data):
        """Submit sales transaction (TrnsSalesSaveWrReq)."""
        return self._make_request(config, self.ENDPOINTS['sales_save'], invoice_data)

    def save_sales(self, config, invoice_data):
        """Submit sales transaction (alias for sales_save)."""
        return self.sales_save(config, invoice_data)

    def save_item(self, config, item_data):
        """Register item with eTIMS (alias for item_save)."""
        return self.item_save(config, item_data)

    # ==================== Purchase Transaction ====================

    def purchase_search(self, config, last_req_dt=None):
        """Search purchase transactions (TrnsPurchaseSalesReq)."""
        data = {
            'lastReqDt': last_req_dt or '20200101000000',
        }
        return self._make_request(config, self.ENDPOINTS['purchase_sales_search'], data)

    def purchase_save(self, config, purchase_data):
        """Submit purchase transaction (TrnsPurchaseSaveReq)."""
        return self._make_request(config, self.ENDPOINTS['purchase_save'], purchase_data)

    # ==================== Stock Management ====================

    def stock_move(self, config, stock_data):
        """Report stock movement (StockMoveReq)."""
        return self._make_request(config, self.ENDPOINTS['stock_move'], stock_data)

    def save_stock_move(self, config, stock_data):
        """Report stock movement (alias for stock_move)."""
        return self.stock_move(config, stock_data)

    def stock_io_save(self, config, stock_io_data):
        """Save stock I/O (StockIOSaveReq)."""
        return self._make_request(config, self.ENDPOINTS['stock_io_save'], stock_io_data)

    def stock_master_save(self, config, stock_master_data):
        """Save stock master (StockMasterSaveReq)."""
        return self._make_request(config, self.ENDPOINTS['stock_master_save'], stock_master_data)

    def save_stock_master(self, config, stock_data):
        """Save stock master (alias for stock_master_save)."""
        return self.stock_master_save(config, stock_data)

    # ==================== Helper Methods ====================

    def format_datetime(self, dt):
        """Format datetime for eTIMS API (YYYYMMDDHHmmss)."""
        if isinstance(dt, str):
            return dt
        return dt.strftime('%Y%m%d%H%M%S')

    def format_date(self, dt):
        """Format date for eTIMS API (YYYYMMDD)."""
        if isinstance(dt, str):
            return dt
        return dt.strftime('%Y%m%d')
