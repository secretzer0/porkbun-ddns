# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-07

### Added
- Initial release of Porkbun Dynamic DNS Client
- Automatic IP detection using ifconfig.me with IPv4 enforcement
- IP caching to avoid unnecessary API calls
- Support for multiple DNS records per domain
- Comprehensive logging with configurable rotation to prevent filesystem overflow
- Debug mode for detailed operation logs
- Manual IP override option
- Robust error handling and validation
- OPNsense integration with native service framework support
- Command-line options for log file location and size management
- Cross-platform support (Linux, Windows, OPNsense)

### Features
- **Log Rotation**: Prevents `/tmp` filesystem overflow on space-constrained systems
- **OPNsense Native**: Integrates with OPNsense's configd service framework
- **Configurable Logging**: Adjustable log file size limits and backup retention
- **IPv4 Focused**: Forces IPv4 detection to avoid IPv6 compatibility issues
- **Production Ready**: Suitable for automated execution via cron or task scheduler

### Documentation
- Comprehensive README with installation guides for Linux, Windows, and OPNsense
- Configuration examples and troubleshooting guides
- API credential setup instructions
- Automation setup for various platforms
