# Odoo Kenya Localization Addons

Private Odoo 18.0 addons for Kenya localization and customizations.

## Structure

```
odoo-addons-kenya/
├── l10n_ke/                 # Kenya base localization
├── l10n_ke_accounting/      # Kenya accounting (KRA compliance)
├── l10n_ke_payroll/         # Kenya payroll (NHIF, NSSF, PAYE)
├── l10n_ke_edi/             # Kenya e-invoicing (TIMS/eTIMS)
└── [custom modules]/        # Client-specific modules
```

## Installation

1. Clone this repository into your Odoo addons path:
   ```bash
   git clone <repo-url> /path/to/odoo/addons/kenya
   ```

2. Add to your Odoo configuration:
   ```
   addons_path = /path/to/odoo/addons,/path/to/odoo/addons/kenya
   ```

3. Update apps list and install modules.

## Odoo Compatibility

- **Odoo Version**: 18.0
- **Base**: OCA/OCB 18.0 (Community Edition)

## License

Proprietary - All Rights Reserved.
This software is confidential and proprietary to VumaCloud.
Unauthorized copying, distribution, or use is strictly prohibited.
