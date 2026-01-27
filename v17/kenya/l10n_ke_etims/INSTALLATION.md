# Installation and Setup Guide

## Prerequisites

1. Odoo v18 Community Edition installed
2. om_account_accountant module installed
3. Valid KRA e-TIMS registration
4. OSCU device registered with KRA

## Installation Steps

### 1. Install the Module

```bash
# Copy the module to your Odoo addons directory
cp -r kra_etims /path/to/odoo/addons/

# Or create a symbolic link
ln -s /path/to/kra_etims /path/to/odoo/addons/kra_etims

# Restart Odoo service
sudo systemctl restart odoo

# Or if running manually
./odoo-bin -c /path/to/odoo.conf
```

### 2. Update Apps List

1. Log in to Odoo as Administrator
2. Go to Apps menu
3. Click "Update Apps List"
4. Confirm the update

### 3. Install the Module

1. In the Apps menu, search for "KRA e-TIMS"
2. Click "Install"
3. Wait for installation to complete

## Initial Configuration

### Step 1: Configure Company Settings

1. Go to **Settings → Accounting**
2. Scroll to **KRA e-TIMS** section
3. Enable **"Enable KRA e-TIMS"**
4. Configure the following:
   - **API URL**: 
     - Sandbox: `https://etims-sbx.kra.go.ke/etims-api`
     - Production: `https://etims.kra.go.ke/etims-api`
   - **Company TIN**: Your tax identification number (e.g., P000000000A)
   - **Branch ID**: Usually "00" for main branch
   - **Device Serial**: Your OSCU device serial number
5. Click **Save**

### Step 2: Initialize Device

1. Go to **e-TIMS → Configuration → Initialize Device**
2. Fill in the form:
   - **Device Name**: e.g., "Main OSCU Device"
   - **Device Serial Number**: Provided by KRA
   - **Company TIN**: Your TIN
   - **Branch ID**: "00" or your branch code
   - **API URL**: Sandbox or Production URL
3. Click **"Initialize Device"**
4. Wait for confirmation
5. Click **"Sync Codes"** to download item classifications

### Step 3: Configure Products

For each product:

1. Go to **Products → Products**
2. Open a product
3. Go to **e-TIMS** tab
4. Configure:
   - **Item Class Code**: Select from list (default: 5020230500)
   - **Item Type**: 
     - Raw Material (1)
     - Finished Product (2)
     - Service (3)
   - **Origin Country Code**: KE for Kenya
   - **Tax Type**: 
     - A: VAT 0% (Exempt)
     - B: VAT 16% (Standard)
     - C: VAT 8% (Reduced)
     - D: No Tax
   - **Package Unit Code**: NT (Not Applicable) or specific unit
5. Click **"Register in e-TIMS"**
6. Wait for confirmation

### Step 4: Configure Taxes

1. Go to **Settings → Accounting → Taxes**
2. For each tax rate, set the **KRA Tax Type**:
   - 16% VAT → B
   - 0% VAT → A
   - 8% VAT → C
   - No tax → D

### Step 5: Configure Customers (B2B)

For business customers:

1. Go to **Contacts**
2. Open customer record
3. Fill in:
   - **VAT/KRA PIN**: Customer's KRA PIN
   - **Customer Type**: B2B
4. Save

## Usage

### Creating and Submitting Invoices

#### Manual Submission

1. Create a customer invoice normally
2. Add products (ensure they're registered in e-TIMS)
3. Set **Payment Type**:
   - Cash (01)
   - Credit (02)
   - Card (03)
   - Mobile Money (04)
4. Validate the invoice
5. Click **"Submit to e-TIMS"**
6. Check the **e-TIMS** tab for:
   - Invoice Number
   - Receipt Signature
   - QR Code
   - Submission Status

#### Automatic Submission

1. Enable **"Auto-Submit Invoices"** in Settings
2. Create and validate invoices normally
3. They will be automatically submitted to e-TIMS

### Handling Credit Notes

1. Create a credit note from an invoice
2. The system automatically links it to the original invoice
3. Submit to e-TIMS as usual
4. The original invoice number is automatically referenced

### Checking Invoice Status

1. Open a submitted invoice
2. Click **"Check e-TIMS Status"**
3. View updated status information

## Testing

### Using Sandbox Environment

1. Set API URL to sandbox: `https://etims-sbx.kra.go.ke/etims-api`
2. Use test credentials provided by KRA
3. Test device initialization
4. Test product registration
5. Test invoice submission
6. Verify QR code generation

### Moving to Production

1. Update API URL to: `https://etims.kra.go.ke/etims-api`
2. Update with production TIN and device serial
3. Re-initialize device in production
4. Re-sync codes
5. Re-register products if needed

## Troubleshooting

### Device Initialization Issues

**Problem**: "Device initialization failed"

**Solutions**:
- Verify TIN is correct format (e.g., P000000000A)
- Check device serial is registered with KRA
- Ensure internet connection is stable
- Verify API URL is correct
- Check Odoo logs for detailed error

### Invoice Submission Issues

**Problem**: "Failed to submit invoice to e-TIMS"

**Solutions**:
- Ensure device is initialized and active
- Verify all products are registered in e-TIMS
- Check that product classifications are valid
- Ensure tax types are configured
- Verify customer TIN format (for B2B)
- Check invoice date is not in the future
- Review Odoo logs for specific error

### Product Registration Issues

**Problem**: "Product registration failed"

**Solutions**:
- Ensure Item Class Code is valid
- Check that Origin Country Code is valid (use ISO codes)
- Verify Tax Type is set
- Ensure product has internal reference (default_code)
- Check product name is not too long (max 200 chars)

## API Rate Limits

The KRA e-TIMS API has rate limits:
- Be patient with API calls
- Don't submit too many products/invoices simultaneously
- Wait for response before making next call

## Data Backup

**Important**: Always backup your Odoo database before:
- Installing the module
- Initializing devices
- Bulk product registration
- Moving to production

## Security

- Keep your TIN and device serial confidential
- Use HTTPS for API communication (built-in)
- Regularly update the module
- Monitor submission logs

## Support

For issues:
1. Check Odoo logs: `/var/log/odoo/odoo-server.log`
2. Review KRA e-TIMS documentation
3. Contact your Odoo partner
4. Verify with KRA support if API issue

## References

- [KRA e-TIMS Portal](https://itax.kra.go.ke/KRA-Portal/)
- [KRA e-TIMS Documentation](https://www.kra.go.ke/en/taxes/etims)
- Odoo v18 Documentation

## Updates

Check for module updates regularly for:
- Bug fixes
- New features
- API changes compliance
- Security patches

---

**Module Version**: 1.0.0  
**Odoo Version**: 18.0  
**Last Updated**: 2025
