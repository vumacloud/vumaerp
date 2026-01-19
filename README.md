# Odoo Rwanda Localization Addons

Private Odoo 18.0 addons for Rwanda localization and customizations.

## Structure

```
odoo-addons-rwanda/
├── l10n_rw/                 # Rwanda base localization
├── l10n_rw_accounting/      # Rwanda accounting (RRA compliance)
├── l10n_rw_payroll/         # Rwanda payroll (RSSB, PAYE)
├── l10n_rw_edi/             # Rwanda e-invoicing (EBM)
└── [custom modules]/        # Client-specific modules
```

## Installation

1. Clone this repository into your Odoo addons path:
   ```bash
   git clone <repo-url> /path/to/odoo/addons/rwanda
   ```

2. Add to your Odoo configuration:
   ```
   addons_path = /path/to/odoo/addons,/path/to/odoo/addons/rwanda
   ```

3. Update apps list and install modules.

## Odoo Compatibility

- **Odoo Version**: 18.0
- **Base**: OCA/OCB 18.0 (Community Edition)

## License

Proprietary - All Rights Reserved.
This software is confidential and proprietary to VumaCloud.
Unauthorized copying, distribution, or use is strictly prohibited.
