# KRA e-TIMS Configuration Examples

## Item Classification Codes (Common Examples)

### General Merchandise
- **5020230500**: General Merchandise and Goods

### Services
- **5020240100**: Professional Services
- **5020240200**: IT Services
- **5020240300**: Consulting Services
- **5020240400**: Legal Services
- **5020240500**: Accounting Services

### Food and Beverages
- **5010110100**: Packaged Food
- **5010110200**: Fresh Food
- **5010110300**: Beverages

### Electronics
- **5020210100**: Computer Equipment
- **5020210200**: Mobile Devices
- **5020210300**: Electronics Accessories

### Clothing
- **5010120100**: Men's Clothing
- **5010120200**: Women's Clothing
- **5010120300**: Children's Clothing

## Tax Type Codes

| Code | Description | Rate | Use Case |
|------|-------------|------|----------|
| A | VAT 0% (Exempt) | 0% | Exempt goods (basic food items, medical supplies, etc.) |
| B | VAT 16% (Standard) | 16% | Standard taxable goods and services |
| C | VAT 8% (Reduced) | 8% | Agricultural inputs, petroleum products |
| D | No Tax | 0% | Out of scope items |

## Item Type Codes

| Code | Description | Use Case |
|------|-------------|----------|
| 1 | Raw Material | Materials used in production |
| 2 | Finished Product | Products ready for sale |
| 3 | Service | Services provided to customers |

## Package Unit Codes

| Code | Description |
|------|-------------|
| BX | Box |
| CT | Carton |
| DZ | Dozen |
| EA | Each |
| KG | Kilogram |
| L | Liter |
| NT | Not Applicable |
| PC | Piece |
| PK | Package |
| RL | Roll |
| SET | Set |
| U | Unit |

## Quantity Unit Codes

| Code | Description |
|------|-------------|
| U | Unit |
| DZ | Dozen |
| KG | Kilogram |
| GRM | Gram |
| L | Liter |
| ML | Milliliter |
| M | Meter |
| CM | Centimeter |
| SQM | Square Meter |

## Payment Type Codes

| Code | Description | Use Case |
|------|-------------|----------|
| 01 | Cash | Cash payments |
| 02 | Credit | Credit/Invoice payments |
| 03 | Card | Credit/Debit card payments |
| 04 | Mobile Money | M-Pesa, Airtel Money, etc. |

## Country Codes (ISO 3166-1 Alpha-2)

| Code | Country |
|------|---------|
| KE | Kenya |
| UG | Uganda |
| TZ | Tanzania |
| RW | Rwanda |
| ET | Ethiopia |
| GB | United Kingdom |
| US | United States |
| CN | China |
| IN | India |
| DE | Germany |

## Sales Type Codes

| Code | Description |
|------|-------------|
| 01 | Normal Sale |
| 02 | Credit Note/Refund |
| 03 | Proforma Invoice |

## Receipt Type Codes

| Code | Description |
|------|-------------|
| S | Sale |
| P | Purchase |
| R | Refund |

## Sales Status Codes

| Code | Description |
|------|-------------|
| 01 | Confirmed |
| 02 | Completed |

## Example Product Configurations

### Example 1: Consulting Service
```
Item Class Code: 5020240300
Item Type: 3 (Service)
Origin Country: KE
Package Unit: NT
Tax Type: B (VAT 16%)
```

### Example 2: Laptop Computer
```
Item Class Code: 5020210100
Item Type: 2 (Finished Product)
Origin Country: CN
Package Unit: EA
Tax Type: B (VAT 16%)
```

### Example 3: Fresh Vegetables
```
Item Class Code: 5010110200
Item Type: 2 (Finished Product)
Origin Country: KE
Package Unit: KG
Tax Type: A (VAT 0% - Exempt)
```

### Example 4: Software License
```
Item Class Code: 5020240200
Item Type: 3 (Service)
Origin Country: KE
Package Unit: NT
Tax Type: B (VAT 16%)
```

## Customer Configuration Examples

### B2B Customer (With KRA PIN)
```
Name: ABC Company Ltd
VAT/KRA PIN: P000123456A
Customer Type: B2B
Country: Kenya
```

### B2C Customer (Without KRA PIN)
```
Name: John Doe
VAT/KRA PIN: (empty)
Customer Type: B2C
Country: Kenya
```

## Invoice Configuration Examples

### Cash Sale
```
Customer: Walk-in Customer
Payment Type: 01 (Cash)
Products: [Product 1, Product 2]
Tax: 16% VAT
```

### Credit Sale to Business
```
Customer: ABC Company Ltd (with PIN)
Payment Type: 02 (Credit)
Products: [Product 1, Product 2]
Tax: 16% VAT
```

### Mobile Money Sale
```
Customer: John Doe
Payment Type: 04 (Mobile Money)
Products: [Product 1]
Tax: 16% VAT
```

## API Endpoints Reference

### Initialization
- **POST** `/initializer/selectInitInfo` - Initialize device

### Code Management
- **POST** `/code/selectCodes` - Get classification codes

### Item Management
- **POST** `/items/saveItem` - Register/Update item
- **POST** `/items/selectItem` - Get item details
- **POST** `/items/selectItemList` - Get item list

### Sales Transaction
- **POST** `/trnsSales/saveSales` - Submit sales invoice
- **POST** `/trnsSales/selectInvoice` - Get invoice details
- **POST** `/trnsSales/selectSalesList` - Get sales list

### Stock Management
- **POST** `/stock/saveStockMaster` - Report stock movement
- **POST** `/stock/selectStockMaster` - Get stock details

## Common Error Codes

| Code | Message | Solution |
|------|---------|----------|
| 001 | Invalid TIN | Check TIN format |
| 002 | Invalid Branch ID | Verify branch ID |
| 003 | Device not initialized | Initialize device first |
| 004 | Invalid item code | Check item classification |
| 005 | Invalid tax type | Use valid tax type code |

## Testing Checklist

- [ ] Device initialized successfully
- [ ] Codes synchronized from KRA
- [ ] Test product registered
- [ ] Tax types configured
- [ ] Test invoice submitted (Sandbox)
- [ ] QR code generated
- [ ] Invoice status retrieved
- [ ] Credit note processed

## Production Deployment Checklist

- [ ] Switch to production API URL
- [ ] Update with production TIN
- [ ] Register production device serial
- [ ] Re-initialize device in production
- [ ] Re-sync classification codes
- [ ] Re-register all products
- [ ] Test with real invoice
- [ ] Monitor first few days closely
- [ ] Train users on submission process
- [ ] Set up backup procedures

## Best Practices

1. **Always test in Sandbox first**
   - Use sandbox environment for all testing
   - Only move to production when confident

2. **Register products before invoicing**
   - Ensure all products are registered in e-TIMS
   - Set correct classifications and tax types

3. **Validate customer data**
   - Verify KRA PINs for B2B customers
   - Ensure complete customer information

4. **Monitor submission status**
   - Check invoice status regularly
   - Review error logs
   - Address failures promptly

5. **Keep records**
   - Backup e-TIMS data regularly
   - Maintain audit trail
   - Document any issues

6. **Stay updated**
   - Monitor KRA announcements
   - Update module regularly
   - Follow compliance changes

## Support Resources

- **KRA e-TIMS Portal**: https://itax.kra.go.ke/KRA-Portal/
- **KRA Help Desk**: 0711099999 or 0734000999
- **Email**: callcentre@kra.go.ke
- **Technical Support**: Via iTax portal

## Useful SQL Queries

### Check submission status of invoices
```sql
SELECT 
    name, 
    partner_id, 
    amount_total, 
    kra_submission_status, 
    kra_invoice_no
FROM account_move 
WHERE move_type = 'out_invoice' 
    AND kra_submission_status = 'submitted'
ORDER BY create_date DESC;
```

### Find unregistered products
```sql
SELECT 
    name, 
    default_code, 
    kra_registered
FROM product_template 
WHERE sale_ok = true 
    AND kra_registered = false;
```

### Check device status
```sql
SELECT 
    name, 
    device_serial, 
    status, 
    initialization_date
FROM kra_etims_device 
ORDER BY create_date DESC;
```
