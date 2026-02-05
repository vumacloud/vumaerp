# VumaERP - African Localization Addons

Private Odoo 17.0 addons for African country localizations and customizations.

## Repository Structure

```
vumaerp/
├── muk_web_theme/           # Base: MuK IT backend theme
├── third_party/odooapps/    # Base: Odoo Mates modules (payroll, accounting)
├── vumaerp_branding/        # VumaERP branding customizations
├── l10n_ke_etims_pos/       # Kenya eTIMS POS & Payment Integration
│
├── kenya/                   # Kenya-specific modules
│   ├── l10n_ke/             # Kenya base localization
│   ├── l10n_ke_etims/       # KRA eTIMS OSCU integration
│   └── l10n_ke_payroll/     # Kenya payroll (PAYE, SHIF, NSSF, Housing Levy)
│
├── uganda/                  # Uganda-specific modules
│   ├── l10n_ug/             # Uganda base localization
│   ├── l10n_ug_efris/       # URA EFRIS e-invoicing integration
│   └── l10n_ug_payroll/     # Uganda payroll (PAYE, NSSF, LST)
│
├── ghana/                   # Ghana-specific modules
│   ├── l10n_gh/             # Ghana base localization
│   ├── l10n_gh_evat/        # GRA E-VAT integration
│   └── l10n_gh_payroll/     # Ghana payroll (PAYE, SSNIT, Tier 2)
│
├── nigeria/                 # Nigeria-specific modules
│   ├── l10n_ng/             # Nigeria base localization
│   ├── l10n_ng_tax/         # FIRS tax integration (VAT, WHT)
│   └── l10n_ng_payroll/     # Nigeria payroll (PAYE, Pension, NHF)
│
├── rwanda/                  # Rwanda-specific modules
│   ├── l10n_rw/             # Rwanda base localization
│   ├── l10n_rw_ebm/         # RRA EBM e-invoicing integration
│   └── l10n_rw_payroll/     # Rwanda payroll (PAYE, RSSB, Maternity)
│
├── ethiopia/                # Ethiopia-specific modules (planned)
└── tanzania/                # Tanzania-specific modules (planned)
```

## Base Modules (All Countries)

| Module | Description |
|--------|-------------|
| `muk_web_theme` | Modern backend theme by MuK IT |
| `third_party/odooapps/om_hr_payroll` | Base payroll module |
| `third_party/odooapps/om_account_accountant` | Full accounting features |
| `vumaerp_branding` | VumaERP branding and customizations |

## Kenya Modules

| Module | Description |
|--------|-------------|
| `l10n_ke` | Base Kenya localization (country data, formats) |
| `l10n_ke_etims` | KRA eTIMS OSCU API integration (22 endpoints) |
| `l10n_ke_etims_pos` | eTIMS POS & Payment integration (SME-focused) |
| `l10n_ke_payroll` | Kenya statutory payroll |

### Kenya Payroll (l10n_ke_payroll)

Statutory deductions (2025 rates):

| Deduction | Rate | Notes |
|-----------|------|-------|
| **PAYE** | 10-35% | Progressive tax bands with KES 2,400 personal relief |
| **SHIF** | 2.75% | Social Health Insurance Fund (replaced NHIF Oct 2024), min KES 300 |
| **NSSF** | 6% | Tier I (up to KES 7,000) + Tier II (up to KES 36,000) |
| **Housing Levy** | 1.5% | Employee + 1.5% Employer |

### Kenya eTIMS (l10n_ke_etims)

#### TIS Registration with KRA

VumaERP is registered as a **Trader Invoicing System (TIS)** with Kenya Revenue Authority:

| Field | Value | Notes |
|-------|-------|-------|
| **TIS Name** | VumaERP | Registered system name |
| **TIS Version** | 2.0.0 | Current TIS version |
| **Serial Number Format** | `VUMAERP{TIN}{BRANCH}` | Auto-generated |

**Serial Number Example:** `VUMAERPP051234567A00`
- `VUMAERP` - TIS prefix
- `P051234567A` - Company KRA PIN
- `00` - Branch ID (00 = main branch)

#### Module Versioning

Format: `{ODOO_MAJOR}.{TIS_MAJOR}.{TIS_MINOR}.{TIS_PATCH}`

- Current Version: `17.2.0.0` (Odoo 17, TIS v2.0.0)
- For KRA registration, report TIS Version: `2.0.0`

#### KRA eTIMS OSCU Features

KRA eTIMS OSCU (Online Sales Control Unit) integration:
- Device registration and verification
- Auto-generated serial numbers (VUMAERP convention)
- Real-time invoice submission
- Item/product registration with UNSPSC classification codes
- Customer PIN validation
- Stock movement reporting
- Purchase transaction submission
- TIS identification in all API requests

### Kenya eTIMS POS & Payment Integration (l10n_ke_etims_pos)

**Critical compliance module** for SMEs using Point of Sale and payment-based workflows.

#### KPMG Tax Alert Compliance (January 2026 Readiness)

Per KPMG Kenya Tax Alert on "eTIMS and the Shift to Data-Driven Income and Expense Validation":

| KPMG Recommendation | Implementation Status |
|---------------------|----------------------|
| **Submit on payment receipt, not invoice posting** | Implemented - Payment-triggered submission |
| **ERP/POS integration with real-time submission** | Implemented - POS and invoice integration |
| **Credit note/refund handling with audit trails** | Implemented - Reason codes and original reference |
| **Full eTIMS coverage across income streams** | Implemented - Invoices + POS orders |
| **Supplier onboarding and PIN validation** | Implemented in base l10n_ke_etims |

#### Key Features

**Payment-Triggered Submission (NOT on invoice posting):**
- Invoices submitted to eTIMS only when payment is received
- Posted but unpaid invoices are NOT submitted
- Ensures eTIMS reflects actual sales, not accrued revenue
- Compliance with KRA position that eTIMS = determinant of taxable income

**POS Integration (SME Critical):**
- Real-time submission when POS payment is completed
- Batch submission at session close for missed orders
- Session-level tracking: submitted/pending/failed statistics
- eTIMS receipt printing with SCU and receipt numbers
- Offline queue capability with automatic retry
- Mobile money (M-Pesa) and card payment detection

**Refund/Return Handling:**
- Credit notes require refund reason code
- POS returns linked to original orders
- Full audit trail for compliance

#### eTIMS Refund Reason Codes

| Code | Reason |
|------|--------|
| 01 | Damage/Defect |
| 02 | Change of Mind |
| 03 | Wrong Item Delivered |
| 04 | Late Delivery |
| 05 | Duplicate Order |
| 06 | Price Dispute |
| 07 | Quantity Dispute |
| 08 | Quality Issues |
| 09 | Order Cancellation |
| 10 | Other |

## Uganda Modules

| Module | Description |
|--------|-------------|
| `l10n_ug` | Base Uganda localization (country data, formats) |
| `l10n_ug_efris` | URA EFRIS e-invoicing integration |
| `l10n_ug_payroll` | Uganda statutory payroll |

### Uganda Payroll (l10n_ug_payroll)

Statutory deductions (2025 rates):

| Deduction | Rate | Notes |
|-----------|------|-------|
| **PAYE** | 0-40% | Progressive tax bands (UGX 235,000 threshold) |
| **NSSF** | 5% + 10% | Employee 5% + Employer 10% of gross |
| **LST** | Varies | Local Service Tax, paid in 4 installments (July-Oct) |

PAYE Tax Bands (Monthly - Residents):
- UGX 0 - 235,000: 0%
- UGX 235,001 - 335,000: 10%
- UGX 335,001 - 410,000: 20%
- UGX 410,001 - 10,000,000: 30%
- Above UGX 10,000,000: 40%

### Uganda EFRIS (l10n_ug_efris)

URA EFRIS (Electronic Fiscal Receipting and Invoicing System) integration:
- Device registration and management
- Real-time invoice submission to URA
- Automatic FDN (Fiscal Document Number) generation
- Credit note handling
- Goods/Services code mapping
- Tax code management (VAT 18%, Exempt, Zero-rated)

## Ghana Modules

| Module | Description |
|--------|-------------|
| `l10n_gh` | Base Ghana localization (country data, 16 regions) |
| `l10n_gh_evat` | GRA E-VAT e-invoicing integration |
| `l10n_gh_payroll` | Ghana statutory payroll |

### Ghana Payroll (l10n_gh_payroll)

Statutory deductions (2025 rates):

| Deduction | Rate | Notes |
|-----------|------|-------|
| **PAYE** | 0-35% | Progressive tax bands (GHS 490 threshold) |
| **SSNIT Tier 1** | 5.5% + 8% | Employee 5.5% + Employer 8% to SSNIT |
| **Tier 2** | 5% | Employer contribution to trustees |
| **Tier 3** | Up to 16.5% | Voluntary provident fund |

PAYE Tax Bands (Monthly - GHS):
- GHS 0 - 490: 0%
- GHS 491 - 600: 5%
- GHS 601 - 730: 10%
- GHS 731 - 3,896: 17.5%
- GHS 3,897 - 20,000: 25%
- GHS 20,001 - 50,000: 30%
- Above GHS 50,000: 35%

### Ghana E-VAT (l10n_gh_evat)

GRA (Ghana Revenue Authority) E-VAT integration:
- Device registration
- Real-time invoice submission
- Tax codes (VAT 15%, NHIL 2.5%, GETFund 2.5%, COVID 1%)
- Exempt and zero-rated supplies

## Nigeria Modules

| Module | Description |
|--------|-------------|
| `l10n_ng` | Base Nigeria localization (country data, 36 states + FCT) |
| `l10n_ng_tax` | FIRS tax integration (VAT, WHT, CIT) |
| `l10n_ng_payroll` | Nigeria statutory payroll |

### Nigeria Payroll (l10n_ng_payroll)

Statutory deductions (2025 rates):

| Deduction | Rate | Notes |
|-----------|------|-------|
| **PAYE** | 7-24% | Progressive tax with CRA relief |
| **Pension** | 8% + 10% | Employee 8% + Employer 10% (minimum) |
| **NHF** | 2.5% | National Housing Fund |
| **NHIS** | 1.75% + 3.25% | Employee + Employer health insurance |

PAYE Tax Bands (Annual - NGN):
- NGN 0 - 300,000: 7%
- NGN 300,001 - 600,000: 11%
- NGN 600,001 - 1,100,000: 15%
- NGN 1,100,001 - 1,600,000: 19%
- NGN 1,600,001 - 3,200,000: 21%
- Above NGN 3,200,000: 24%

CRA (Consolidated Relief Allowance): Higher of NGN 200,000 or 1% of gross + 20% of gross

### Nigeria Tax (l10n_ng_tax)

FIRS (Federal Inland Revenue Service) tax integration:
- VAT management (7.5%)
- Withholding Tax (5-10% by transaction type)
- Company Income Tax (0-30% by company size)
- Tax code management
- TCC (Tax Clearance Certificate) tracking

## Rwanda Modules

| Module | Description |
|--------|-------------|
| `l10n_rw` | Base Rwanda localization (country data, formats) |
| `l10n_rw_ebm` | RRA EBM e-invoicing integration |
| `l10n_rw_payroll` | Rwanda statutory payroll |

### Rwanda EBM (l10n_rw_ebm)

RRA (Rwanda Revenue Authority) EBM (Electronic Billing Machine) integration:
- Device registration and management
- Real-time invoice submission to RRA
- Credit note handling with original reference
- Tax code management (VAT 18%, Exempt, Zero-rated)
- Stock management integration

### Rwanda Payroll (l10n_rw_payroll)

Statutory deductions (2025 rates):

| Deduction | Rate | Notes |
|-----------|------|-------|
| **PAYE** | 0-30% | Progressive tax bands |
| **RSSB Pension** | 3% + 5% | Employee 3% + Employer 5% |
| **RSSB Medical** | 0.5% + 0.5% | Employee + Employer |
| **Maternity** | 0.3% | Employer only |

## Installation

All VumaERP modules are installed to `/opt/odoo/addons` - this is the **only** addons directory used.

1. Clone this repository to a staging location:
   ```bash
   git clone https://github.com/vumacloud/vumaerp.git /opt/vumaerp
   ```

2. Copy/symlink the required modules to `/opt/odoo/addons` based on country:

   **Kenya:**
   ```bash
   # Base modules
   cp -r /opt/vumaerp/muk_web_theme /opt/odoo/addons/
   cp -r /opt/vumaerp/third_party/odooapps/* /opt/odoo/addons/
   cp -r /opt/vumaerp/vumaerp_branding /opt/odoo/addons/

   # Kenya-specific modules
   cp -r /opt/vumaerp/kenya/* /opt/odoo/addons/
   cp -r /opt/vumaerp/l10n_ke_etims_pos /opt/odoo/addons/
   ```

   **Uganda:**
   ```bash
   # Base modules (same as above)
   # Uganda-specific modules
   cp -r /opt/vumaerp/uganda/* /opt/odoo/addons/
   ```

   **Ghana:**
   ```bash
   # Base modules (same as above)
   # Ghana-specific modules
   cp -r /opt/vumaerp/ghana/* /opt/odoo/addons/
   ```

   **Nigeria:**
   ```bash
   # Base modules (same as above)
   # Nigeria-specific modules
   cp -r /opt/vumaerp/nigeria/* /opt/odoo/addons/
   ```

   **Rwanda:**
   ```bash
   # Base modules (same as above)
   # Rwanda-specific modules
   cp -r /opt/vumaerp/rwanda/* /opt/odoo/addons/
   ```

3. Ensure Odoo config points to the addons directory:
   ```ini
   addons_path = /opt/odoo/addons
   ```

4. Restart Odoo and update apps list, then install required modules.

## Odoo Compatibility

- **Odoo Version**: 17.0
- **Base**: OCA/OCB 17.0 (Community Edition)

## Compliance References

### Kenya
- KPMG Tax Alert: "eTIMS and the Shift to Data-Driven Income and Expense Validation"
- Finance Act, 2023 (expense disallowance for non-eTIMS transactions)
- Electronic Tax Invoice Regulations, 2024
- KRA eTIMS OSCU API Documentation

### Uganda
- URA EFRIS Implementation Guidelines
- VAT Act (Electronic Fiscal Devices)

### Ghana
- GRA E-VAT System Requirements
- VAT Act, 2013 (as amended)

### Nigeria
- FIRS VAT Guidelines
- Finance Act, 2023

### Rwanda
- RRA EBM Implementation Guidelines
- Law on Tax Procedures

## License

Proprietary - All Rights Reserved.
This software is confidential and proprietary to VumaCloud.
Unauthorized copying, distribution, or use is strictly prohibited.
