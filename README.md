# VumaERP - African Localization Addons

Private Odoo 18.0 addons for African country localizations and customizations.

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
├── ethiopia/                # Ethiopia-specific modules (planned)
├── uganda/                  # Uganda-specific modules (planned)
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

   **Ethiopia:**
   ```ini
   addons_path = /opt/odoo/addons,/opt/vumaerp,/opt/vumaerp/ethiopia
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

- **Odoo Version**: 18.0
- **Base**: OCA/OCB 18.0 (Community Edition)

## License

Proprietary - All Rights Reserved.
This software is confidential and proprietary to VumaCloud.
Unauthorized copying, distribution, or use is strictly prohibited.
