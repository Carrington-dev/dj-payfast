# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-12-04
## [0.1.1] - 2025-12-04

### Added
- Initial release of dj-payfast
- PayFastPayment model for tracking payments
- PayFastNotification model for logging ITN webhooks
- PayFastPaymentForm for generating payment forms
- PayFastNotifyView for handling webhooks
- Signature generation and verification utilities
- Django admin integration
- Comprehensive documentation
- Test suite with pytest
- Support for Django 3.2 - 5.0
- Support for Python 3.8 - 3.12

### Security
- Built-in signature verification
- IP address validation
- Server-side validation with PayFast

[Unreleased]: https://github.com/carrington-dev/dj-payfast/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/carrington-dev/dj-payfast/releases/tag/v0.1.0
[0.1.1]: https://github.com/carrington-dev/dj-payfast/releases/tag/v0.1.1