# Odoo Tanzania Localization Addons

Private Odoo 18.0 addons for Tanzania localization and customizations.

## Structure

```
odoo-addons-tanzania/
├── l10n_tz/                 # Tanzania base localization
├── l10n_tz_accounting/      # Tanzania accounting (TRA compliance)
├── l10n_tz_payroll/         # Tanzania payroll (NSSF, PAYE, SDL, WCF)
├── l10n_tz_edi/             # Tanzania e-invoicing (VFD/EFD)
└── [custom modules]/        # Client-specific modules
```

## Installation

1. Clone this repository into your Odoo addons path:
   ```bash
   git clone <repo-url> /path/to/odoo/addons/tanzania
   ```

2. Add to your Odoo configuration:
   ```
   addons_path = /path/to/odoo/addons,/path/to/odoo/addons/tanzania
   ```

3. Update apps list and install modules.

## Odoo Compatibility

- **Odoo Version**: 18.0
- **Base**: OCA/OCB 18.0 (Community Edition)

## License

Proprietary - All Rights Reserved.
This software is confidential and proprietary to VumaCloud.
Unauthorized copying, distribution, or use is strictly prohibited.
