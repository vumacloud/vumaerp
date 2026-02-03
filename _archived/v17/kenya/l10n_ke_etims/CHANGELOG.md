# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-27

### Added
- Initial release of KRA e-TIMS Integration for Odoo v18 Community Edition
- Device management functionality
  - Device registration and initialization
  - Multi-device support
  - Device status tracking
- Product/Item management
  - Product registration with e-TIMS
  - Item classification support
  - Tax type configuration
  - Package and quantity unit codes
- Invoice submission
  - Automatic invoice submission on validation
  - Manual invoice submission
  - Support for customer invoices and credit notes
  - QR code generation for receipts
  - Invoice status tracking
- Configuration management
  - Company-level e-TIMS settings
  - Sandbox and production environment support
  - Branch management
- Code synchronization
  - Sync item classifications from KRA
  - Auto-update classification codes
- Multi-company support
  - Separate e-TIMS configuration per company
  - Company-specific device management
- Customer management
  - B2B and B2C customer types
  - KRA PIN management
  - Customer TIN validation
- Payment type support
  - Cash, Credit, Card, Mobile Money
- Comprehensive error handling
  - User-friendly error messages
  - Detailed logging for troubleshooting
- Documentation
  - README with feature overview
  - Installation guide
  - Configuration examples
  - API testing script

### Security
- Secure API communication over HTTPS
- TIN and device serial protection
- Role-based access control

### Technical
- Built for Odoo v18 Community Edition
- Compatible with om_account_accountant module
- RESTful API integration with KRA e-TIMS
- Proper transaction handling
- Database constraints for data integrity

## [Unreleased]

### Planned Features
- Bulk product registration wizard
- Stock movement automatic reporting
- Advanced reporting dashboard
- Invoice print templates with e-TIMS data
- SMS notifications for invoice submission
- Email integration for e-receipts
- Support for more payment types
- Multi-currency support
- Integration with KRA iTax portal
- Advanced invoice search and filtering
- Export functionality for e-TIMS data
- Scheduled synchronization tasks
- Mobile app support
- API rate limiting handling
- Retry mechanism for failed submissions

### Known Issues
- None reported in initial release

### Future Enhancements
- Support for purchase invoices
- Import invoice functionality
- Customs declaration support
- Tourism tax handling
- Excise duty management
- Insurance premium management
- More detailed tax reports
- Audit trail improvements
- Performance optimizations
- Enhanced error recovery

---

## Version History

- **1.0.0** (2025-01-27): Initial Release

## Support

For support, please contact:
- Your Odoo partner
- KRA Help Desk: 0711099999 or 0734000999
- Email: callcentre@kra.go.ke

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This module is licensed under LGPL-3. See LICENSE file for details.
