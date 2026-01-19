# Odoo Uganda Localization Addons

Private Odoo 18.0 addons for Uganda localization and customizations.

## Structure

```
odoo-addons-uganda/
├── l10n_ug/                 # Uganda base localization
├── l10n_ug_accounting/      # Uganda accounting (URA compliance)
├── l10n_ug_payroll/         # Uganda payroll (NSSF, PAYE, LST)
├── l10n_ug_edi/             # Uganda e-invoicing (EFRIS)
└── [custom modules]/        # Client-specific modules
```

## Installation

1. Clone this repository into your Odoo addons path:
   ```bash
   git clone <repo-url> /path/to/odoo/addons/uganda
   ```

2. Add to your Odoo configuration:
   ```
   addons_path = /path/to/odoo/addons,/path/to/odoo/addons/uganda
   ```

3. Update apps list and install modules.

## Odoo Compatibility

- **Odoo Version**: 18.0
- **Base**: OCA/OCB 18.0 (Community Edition)

## License

Proprietary - All Rights Reserved.
This software is confidential and proprietary to VumaCloud.
Unauthorized copying, distribution, or use is strictly prohibited.
