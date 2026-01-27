# KRA e-TIMS Integration for Odoo v18

## Overview

This module provides comprehensive integration with Kenya Revenue Authority's e-TIMS (Tax Invoice Management System) through the OSCU (Online Sales Control Unit) interface for Odoo v18 Community Edition.

## Features

- **Device Management**: Register and manage multiple OSCU devices
- **Automatic Invoice Submission**: Submit customer invoices to e-TIMS automatically or manually
- **Product Registration**: Register products with KRA e-TIMS system
- **Item Classification**: Sync and manage KRA item classification codes
- **Tax Type Management**: Configure tax types according to KRA requirements
- **Receipt Generation**: Generate e-TIMS compliant receipts with QR codes
- **Status Tracking**: Track submission status of invoices
- **Credit Note Support**: Handle refunds and credit notes
- **Multi-Company Support**: Manage multiple companies with different e-TIMS configurations

## Installation

1. Copy the `kra_etims` folder to your Odoo addons directory
2. Update the addons list: Go to Apps → Update Apps List
3. Search for "KRA e-TIMS Integration"
4. Click Install

## Configuration

### Initial Setup

1. **Enable e-TIMS Integration**
   - Go to Settings → Accounting → KRA e-TIMS
   - Enable "Enable KRA e-TIMS"
   - Enter your API URL (Sandbox or Production)
   - Enter your Company TIN
   - Enter your Branch ID (usually "00" for main branch)

2. **Initialize Device**
   - Go to e-TIMS → Configuration → Initialize Device
   - Enter device details:
     - Device Name
     - Device Serial Number (provided by KRA)
     - Company TIN
     - Branch ID
   - Click "Initialize Device"

3. **Sync Codes**
   - After device initialization, click "Sync Codes" to download item classifications from KRA
   - This will populate the Item Classifications list

### Product Configuration

For each product you want to sell:

1. Go to the product form
2. Navigate to the "e-TIMS" tab
3. Configure:
   - **Item Class Code**: Select appropriate classification (default: 5020230500 for general merchandise)
   - **Item Type**: Raw Material, Finished Product, or Service
   - **Origin Country Code**: Default is "KE" for Kenya
   - **Tax Type**: Select appropriate VAT rate
   - **Package Unit Code**: Select packaging unit
4. Click "Register in e-TIMS" to register the product with KRA

### Customer Configuration

For B2B customers with KRA PIN:
1. Go to customer form
2. Enter the customer's KRA PIN in the "VAT" or "KRA PIN" field
3. Set Customer Type to "B2B"

### Invoice Submission

**Manual Submission:**
1. Create and validate a customer invoice
2. Click "Submit to e-TIMS" button
3. The invoice will be submitted and you'll receive the e-TIMS invoice number

**Automatic Submission:**
1. Enable "Auto-Submit Invoices" in Settings
2. Invoices will be automatically submitted when validated

## API Endpoints Used

This module integrates with the following KRA e-TIMS API endpoints:

- `/initializer/selectInitInfo` - Device initialization
- `/code/selectCodes` - Code synchronization
- `/items/saveItem` - Product registration
- `/trnsSales/saveSales` - Invoice submission
- `/trnsSales/selectInvoice` - Invoice status retrieval
- `/stock/saveStockMaster` - Stock movement reporting

## Environment URLs

**Sandbox (Testing):**
```
https://etims-sbx.kra.go.ke/etims-api
```

**Production:**
```
https://etims.kra.go.ke/etims-api
```

## Tax Type Codes

- **A**: VAT 0% (Exempt)
- **B**: VAT 16% (Standard Rate)
- **C**: VAT 8% (Reduced Rate)
- **D**: No Tax

## Item Type Codes

- **1**: Raw Material
- **2**: Finished Product
- **3**: Service

## Payment Type Codes

- **01**: Cash
- **02**: Credit
- **03**: Card
- **04**: Mobile Money

## Common Item Classifications

- **5020230500**: General Merchandise
- **5020240100**: Professional Services

(More classifications can be synced from KRA)

## Troubleshooting

### Device Initialization Fails

- Verify your TIN, Branch ID, and Device Serial are correct
- Ensure you're using the correct API URL (Sandbox vs Production)
- Check your internet connection
- Verify the device serial is registered with KRA

### Invoice Submission Fails

- Ensure the device is initialized and active
- Verify all products on the invoice are registered in e-TIMS
- Check that all required fields are filled
- Ensure tax types are configured correctly

### Product Registration Fails

- Verify the Item Class Code is valid
- Check that all required product fields are filled
- Ensure the product has a valid default code (internal reference)

## Support

For support and issues:
- Check the Odoo log files for detailed error messages
- Verify your KRA e-TIMS credentials and device registration
- Contact your Odoo partner or developer

## Requirements

- Odoo v18 Community Edition
- om_account_accountant module (https://apps.odoo.com/apps/modules/18.0/om_account_accountant)
- Valid KRA e-TIMS registration and OSCU device

## License

LGPL-3

## Credits

Developed for Odoo v18 Community Edition with KRA e-TIMS OSCU integration.

## Changelog

### Version 1.0.0
- Initial release
- Device management
- Product registration
- Invoice submission
- Code synchronization
- Multi-company support
