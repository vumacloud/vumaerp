# Odoo Ethiopia Localization Addons

Private Odoo 18.0 addons for Ethiopia localization and customizations.

## Structure

```
odoo-addons-ethiopia/
├── l10n_et/                 # Ethiopia base localization
├── l10n_et_accounting/      # Ethiopia accounting (ERCA compliance)
├── l10n_et_payroll/         # Ethiopia payroll (pension, income tax)
├── l10n_et_edi/             # Ethiopia e-invoicing
└── [custom modules]/        # Client-specific modules
```

## Installation

1. Clone this repository into your Odoo addons path:
   ```bash
   git clone <repo-url> /path/to/odoo/addons/ethiopia
   ```

2. Add to your Odoo configuration:
   ```
   addons_path = /path/to/odoo/addons,/path/to/odoo/addons/ethiopia
   ```

3. Update apps list and install modules.

## Odoo Compatibility

- **Odoo Version**: 18.0
- **Base**: OCA/OCB 18.0 (Community Edition)

## License

Proprietary - All Rights Reserved.
This software is confidential and proprietary to VumaCloud.
Unauthorized copying, distribution, or use is strictly prohibited.
