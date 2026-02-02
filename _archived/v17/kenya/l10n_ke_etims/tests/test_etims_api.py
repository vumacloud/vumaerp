#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KRA e-TIMS API Testing Script

This script can be used to test the e-TIMS API endpoints independently
before integrating with Odoo.

Usage:
    python test_etims_api.py
"""

import json
import requests
from datetime import datetime

# Configuration
BASE_URL = "https://etims-sbx.kra.go.ke/etims-api"  # Sandbox
TIN = "P000000000A"  # Replace with your TIN
BHF_ID = "00"  # Branch ID
DEVICE_SERIAL = "SN0000000001"  # Replace with your device serial


def make_request(endpoint, data):
    """Make HTTP request to e-TIMS API"""
    url = f"{BASE_URL}/{endpoint}"
    
    headers = {
        'Content-Type': 'application/json',
        'tin': TIN,
        'bhfId': BHF_ID,
    }
    
    # Add timestamp
    data['reqDt'] = datetime.now().strftime('%Y%m%d%H%M%S')
    
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint}")
    print(f"{'='*60}")
    print(f"Request: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        print(f"\nResponse: {json.dumps(result, indent=2)}")
        
        if result.get('resultCd') == '000':
            print("\n✓ SUCCESS")
        else:
            print(f"\n✗ ERROR: {result.get('resultMsg')}")
        
        return result
        
    except Exception as e:
        print(f"\n✗ EXCEPTION: {str(e)}")
        return None


def test_device_initialization():
    """Test device initialization"""
    data = {
        'tin': TIN,
        'bhfId': BHF_ID,
        'dvcSrlNo': DEVICE_SERIAL,
    }
    return make_request('initializer/selectInitInfo', data)


def test_select_codes():
    """Test code selection (item classifications)"""
    data = {
        'tin': TIN,
        'bhfId': BHF_ID,
        'lastReqDt': '20200101000000',
        'cdCls': '01',  # Item Classification
    }
    return make_request('code/selectCodes', data)


def test_save_item():
    """Test product/item registration"""
    data = {
        'tin': TIN,
        'bhfId': BHF_ID,
        'itemCd': 'TEST001',
        'itemClsCd': '5020230500',
        'itemTyCd': '2',  # Finished Product
        'itemNm': 'Test Product',
        'itemStdNm': 'Test Product',
        'orgnNatCd': 'KE',
        'pkgUnitCd': 'NT',
        'qtyUnitCd': 'U',
        'taxTyCd': 'B',  # VAT 16%
        'btchNo': None,
        'bcd': None,
        'dftPrc': 1000.00,
        'addInfo': 'Test product for API testing',
        'sftyQty': 0,
        'isrcAplcbYn': 'N',
        'useYn': 'Y',
        'regrNm': 'Test User',
        'regrId': '1',
        'modrNm': 'Test User',
        'modrId': '1',
    }
    return make_request('items/saveItem', data)


def test_save_sales():
    """Test sales invoice submission"""
    data = {
        'tin': TIN,
        'bhfId': BHF_ID,
        'invcNo': 1,
        'orgInvcNo': 0,
        'custTin': None,
        'custNm': 'Test Customer',
        'salesTyCd': '01',  # Normal Sale
        'rcptTyCd': 'S',
        'pmtTyCd': '01',  # Cash
        'salesSttsCd': '02',  # Completed
        'cfmDt': datetime.now().strftime('%Y%m%d%H%M%S'),
        'salesDt': datetime.now().strftime('%Y%m%d'),
        'stockRlsDt': None,
        'cnclReqDt': None,
        'cnclDt': None,
        'rfdDt': None,
        'rfdRsnCd': None,
        'totItemCnt': 1,
        'taxblAmtA': 0,
        'taxblAmtB': 1000.00,
        'taxblAmtC': 0,
        'taxblAmtD': 0,
        'taxRtA': 0,
        'taxRtB': 16,
        'taxRtC': 8,
        'taxRtD': 0,
        'taxAmtA': 0,
        'taxAmtB': 160.00,
        'taxAmtC': 0,
        'taxAmtD': 0,
        'totTaxblAmt': 1000.00,
        'totTaxAmt': 160.00,
        'totAmt': 1160.00,
        'prchrAcptcYn': 'N',
        'remark': 'Test Invoice',
        'regrId': '1',
        'regrNm': 'Test User',
        'modrNm': 'Test User',
        'modrId': '1',
        'receipt': {
            'custTin': None,
            'custMblNo': None,
            'rptNo': 0,
        },
        'itemList': [{
            'itemSeq': 1,
            'itemCd': 'TEST001',
            'itemClsCd': '5020230500',
            'itemNm': 'Test Product',
            'bcd': None,
            'pkgUnitCd': 'NT',
            'pkg': 1,
            'qtyUnitCd': 'U',
            'qty': 1,
            'prc': 1000.00,
            'splyAmt': 1000.00,
            'dcRt': 0,
            'dcAmt': 0,
            'isrccCd': None,
            'isrccNm': None,
            'isrcRt': 0,
            'isrcAmt': 0,
            'taxTyCd': 'B',
            'taxblAmt': 1000.00,
            'taxTyCdNm': 'VAT 16%',
            'taxRt': 16,
            'taxAmt': 160.00,
            'totAmt': 1160.00,
            'itemExprDt': None,
        }],
    }
    return make_request('trnsSales/saveSales', data)


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("KRA e-TIMS API Testing Script")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  Base URL: {BASE_URL}")
    print(f"  TIN: {TIN}")
    print(f"  Branch ID: {BHF_ID}")
    print(f"  Device Serial: {DEVICE_SERIAL}")
    
    tests = [
        ("Device Initialization", test_device_initialization),
        ("Select Codes (Classifications)", test_select_codes),
        ("Save Item (Product Registration)", test_save_item),
        ("Save Sales (Invoice Submission)", test_save_sales),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            success = result and result.get('resultCd') == '000'
            results.append((test_name, success))
        except Exception as e:
            print(f"\nTest failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    print(f"\nTotal: {passed}/{total} tests passed")


if __name__ == '__main__':
    main()
