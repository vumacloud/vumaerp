# VumaCloud ERP - African Localization

Private Odoo 18.0 CE localization addons for East African markets.

## Country Branches

| Country | Branch | Module | Tax Authority | E-Invoicing |
|---------|--------|--------|---------------|-------------|
| 🇰🇪 Kenya | [`claude/kenya-v18-be0Kk`](../../tree/claude/kenya-v18-be0Kk) | l10n_ke | KRA | eTIMS |
| 🇪🇹 Ethiopia | [`claude/ethiopia-v18-be0Kk`](../../tree/claude/ethiopia-v18-be0Kk) | l10n_et | ERCA | - |
| 🇺🇬 Uganda | [`claude/uganda-v18-be0Kk`](../../tree/claude/uganda-v18-be0Kk) | l10n_ug | URA | EFRIS |
| 🇹🇿 Tanzania | [`claude/tanzania-v18-be0Kk`](../../tree/claude/tanzania-v18-be0Kk) | l10n_tz | TRA | VFD/EFD |
| 🇷🇼 Rwanda | [`claude/rwanda-v18-be0Kk`](../../tree/claude/rwanda-v18-be0Kk) | l10n_rw | RRA | EBM |

## Architecture

```
vumaerp/
├── main                     # This overview
├── claude/kenya-v18-*       # Kenya localization addons
├── claude/ethiopia-v18-*    # Ethiopia localization addons
├── claude/uganda-v18-*      # Uganda localization addons
├── claude/tanzania-v18-*    # Tanzania localization addons
└── claude/rwanda-v18-*      # Rwanda localization addons
```

Each country branch contains:
- **l10n_XX/** - Base localization module
- **l10n_XX_accounting/** - Country-specific accounting (planned)
- **l10n_XX_payroll/** - Country-specific payroll (planned)
- **l10n_XX_edi/** - E-invoicing integration (planned)

## Odoo Compatibility

- **Odoo Version**: 18.0
- **Base**: OCA/OCB 18.0 (Community Edition)
- **License**: Proprietary (addons only)

## Deployment

Each country branch is deployed independently:

```bash
# Clone specific country branch
git clone -b claude/kenya-v18-be0Kk https://github.com/vumacloud/vumaerp.git kenya-addons

# Add to Odoo addons path
addons_path = /path/to/odoo/addons,/path/to/kenya-addons
```

## License

Proprietary - All Rights Reserved.
Copyright (c) 2026 VumaCloud.

The localization addons in this repository are proprietary software.
Odoo core (OCA/OCB) is used under LGPL-3.0 as a separate dependency.
