# VumaERP - African Localization Addons

Private Odoo 17.0 addons for African country localizations and customizations.

## Repository Structure

```
vumaerp/
├── muk_web_theme/           # Base: MuK IT backend theme
├── third_party/odooapps/    # Base: Odoo Mates modules (payroll, accounting)
├── vuma_config/             # Base: Environment configuration (.env support)
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
├── ethiopia/                # Ethiopia-specific modules (planned)
├── tanzania/                # Tanzania-specific modules (planned)
└── rwanda/                  # Rwanda-specific modules (planned)
```

## Base Modules (All Countries)

| Module | Description |
|--------|-------------|
| `muk_web_theme` | Modern backend theme by MuK IT |
| `third_party/odooapps/om_hr_payroll` | Base payroll module |
| `third_party/odooapps/om_account_accountant` | Full accounting features |
| `vuma_config` | Environment-based configuration with .env file support |

## Kenya Modules

| Module | Description |
|--------|-------------|
| `l10n_ke` | Base Kenya localization (country data, formats) |
| `l10n_ke_etims` | KRA eTIMS OSCU API integration (22 endpoints) |
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

KRA eTIMS OSCU (Online Sales Control Unit) integration:
- Device registration and verification
- Real-time invoice submission
- Item/product registration with classification codes
- Customer PIN validation
- Stock movement reporting
- Purchase transaction submission

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

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/vumacloud/vumaerp.git /opt/vumaerp
   ```

2. Configure Odoo addons path based on country:

   **Kenya:**
   ```ini
   addons_path = /opt/odoo/addons,/opt/vumaerp,/opt/vumaerp/kenya
   ```

   **Uganda:**
   ```ini
   addons_path = /opt/odoo/addons,/opt/vumaerp,/opt/vumaerp/uganda
   ```

   **Ghana:**
   ```ini
   addons_path = /opt/odoo/addons,/opt/vumaerp,/opt/vumaerp/ghana
   ```

   **Nigeria:**
   ```ini
   addons_path = /opt/odoo/addons,/opt/vumaerp,/opt/vumaerp/nigeria
   ```

3. Update apps list and install required modules.

## Environment Configuration

The `vuma_config` module supports `.env` files for configuration:

```bash
# /etc/odoo/.env or ~/.odoo/.env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=secret
```

## Odoo Compatibility

- **Odoo Version**: 17.0
- **Base**: OCA/OCB 17.0 (Community Edition)

## License

Proprietary - All Rights Reserved.
This software is confidential and proprietary to VumaCloud.
Unauthorized copying, distribution, or use is strictly prohibited.
