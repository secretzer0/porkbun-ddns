# Porkbun Dynamic DNS Client

[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/release/secretzer0/porkbun-ddns.svg)](https://github.com/secretzer0/porkbun-ddns/releases)
[![GitHub stars](https://img.shields.io/github/stars/secretzer0/porkbun-ddns.svg)](https://github.com/secretzer0/porkbun-ddns/stargazers)

A focused Python script for automatic Porkbun DNS updates on OPNsense systems. **Fills the gap where OPNsense's ddclient package doesn't yet support Porkbun.** Born from frustration with expensive domain API pricing and the need for reliable Porkbun integration.

**Perfect for:**
- **OPNsense users needing Porkbun support** (not available in ddclient package)
- Users who switched from expensive DNS providers to Porkbun
- Homelab environments requiring reliable, minimal-dependency solutions
- Anyone wanting native OPNsense service integration

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Installation](#installation)
  - [Linux Installation](#linux-installation)
  - [Windows Installation](#windows-installation)
  - [OPNsense Installation](#opnsense-installation)
- [Usage](#usage)
- [Automation](#automation)
- [Logging](#logging)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

- Automatic IP detection using ifconfig.me
- IP caching to avoid unnecessary API calls
- Support for multiple DNS records per domain
- Comprehensive logging with debug mode
- Manual IP override option
- IPv4 enforcement to prevent IPv6 issues
- Robust error handling and validation
- Log rotation to prevent filesystem overflow

## Prerequisites

- Python 3.6 or higher
- A Porkbun account with API access enabled
- API credentials from your Porkbun account

## Configuration

Create a `config.json` file with your Porkbun API credentials and domain settings:

```json
{
    "endpoint": "https://api-ipv4.porkbun.com/api/json/v3",
    "apikey": "pk1_key",
    "secretapikey": "sk1_key",
    "domain": "example.com",
    "records": [
        { "name": "www" },
        { "name": "home" },
        { "name": "@" }
    ]
}
```

### Configuration Options

- `endpoint`: The Porkbun API endpoint (defaults to https://api-ipv4.porkbun.com/api/json/v3)
- `apikey`: Your Porkbun API key (format: pk1_...)
- `secretapikey`: Your Porkbun secret API key (format: sk1_...)
- `domain`: The domain you want to update
- `records`: Array of DNS records to manage
  - `name`: The subdomain name (use "@" for the root domain)

### Getting API Credentials

1. Log into your Porkbun account
2. Go to Account → API Access
3. Enable API access for your domain
4. Generate your API key and secret key

## Installation

### Linux Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/secretzer0/porkbun-ddns.git
   cd porkbun-ddns
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Windows Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/secretzer0/porkbun-ddns.git
   cd porkbun-ddns
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### OPNsense Installation

For OPNsense firewall/router systems, follow these steps to integrate the script with the system's service framework:

1. **Enable SSH access** on your OPNsense system:
   - Go to System → Settings → Administration
   - Enable "Secure Shell" and configure as needed

2. **Copy the script to the OPNsense scripts directory**:
   ```bash
   scp porkbun_ddns.py root@opnsense-ip:/usr/local/opnsense/scripts/dns/
   ```
   Or copy it manually via SSH/SCP to `/usr/local/opnsense/scripts/dns/`

3. **Make the script executable**:
   ```bash
   ssh root@opnsense-ip
   chmod +x /usr/local/opnsense/scripts/dns/porkbun_ddns.py
   ```

4. **Create the OPNsense action configuration file**:
   ```bash
   cat > /usr/local/opnsense/service/conf/actions.d/actions_porkbun.conf << 'EOF'
   [update]
   command:/usr/local/opnsense/scripts/dns/porkbun_ddns.py
   parameters:/usr/local/etc/porkbun-ddns.json /tmp/porkbun-ddns.cache
   type:script
   message:updating ddns
   description:PorkBun DDNS
   EOF
   ```
   **Note:** Ensure the command path matches the exact filename (`porkbun_ddns.py`, not `porkbun-ddns.py`)

5. **Set proper permissions for the action file**:
   ```bash
   chmod 644 /usr/local/opnsense/service/conf/actions.d/actions_porkbun.conf
   ```

6. **Create your configuration file**:
   ```bash
   cat > /usr/local/etc/porkbun-ddns.json << 'EOF'
   {
       "endpoint": "https://api-ipv4.porkbun.com/api/json/v3",
       "apikey": "your_actual_pk1_key_here",
       "secretapikey": "your_actual_sk1_key_here",
       "domain": "yourdomain.com",
       "records": [
           { "name": "www" },
           { "name": "home" },
           { "name": "@" }
       ]
   }
   EOF
   ```

7. **Set proper permissions for the configuration file**:
   ```bash
   chmod 644 /usr/local/etc/porkbun-ddns.json
   ```

8. **Restart the configuration daemon**:
   ```bash
   service configd restart
   ```

9. **Set up automated execution via Cron**:
   - In the OPNsense web interface, go to **System → Settings → Cron**
   - Click the **+** button to add a new cron job
   - Configure your desired interval (e.g., `*/5 * * * *` for every 5 minutes)
   - For the **Command** field, select **"PorkBun DDNS"** from the dropdown
   - Save the configuration

10. **Monitor execution**:
    - Log files will be stored in `/tmp/porkbun.ddns.log`
    - Check logs with: `tail -f /tmp/porkbun.ddns.log`

#### OPNsense-specific Notes

- Python 3 is pre-installed on OPNsense systems
- The `requests` library is typically available by default
- If you encounter import errors, install requests with: `python3 -m pip install requests`
- **Logging**: Default `/tmp` location is cleared on reboot; consider using `--log-file /var/log/porkbun.ddns.log` for persistence
- **Log rotation**: Automatically prevents `/tmp` filesystem overflow with 1MB max file size and 3 backups (4MB total max)

#### Testing the OPNsense Installation

```bash
# Test the script manually first
/usr/local/opnsense/scripts/dns/porkbun_ddns.py /usr/local/etc/porkbun-ddns.json /tmp/porkbun-ddns.cache --debug

# Test via the OPNsense action system
configctl porkbun update
```

## Usage

### Basic Usage

```bash
python porkbun_ddns.py config.json ip_cache.txt
```

### Advanced Options

```bash
# Enable debug logging
python porkbun_ddns.py config.json ip_cache.txt --debug

# Specify IP address manually
python porkbun_ddns.py config.json ip_cache.txt -i 192.168.1.100

# Custom log file location and size limits
python porkbun_ddns.py config.json ip_cache.txt --log-file /var/log/porkbun.ddns.log --log-max-size 2 --log-backup-count 5

# Show help
python porkbun_ddns.py --help
```

### Parameters

- `config`: Path to your configuration JSON file
- `cache`: Path to IP cache file (will be created if it doesn't exist)
- `-i, --ip`: Manually specify IP address instead of auto-detection
- `--debug`: Enable verbose debug logging
- `--log-file`: Custom log file path (default: /tmp/porkbun.ddns.log)
- `--log-max-size`: Maximum log file size in MB before rotation (default: 1)
- `--log-backup-count`: Number of backup log files to keep (default: 3)

## Automation

### Linux/macOS Cron

Add to your crontab to run every 5 minutes:

```bash
crontab -e
```

Add this line:
```
*/5 * * * * /usr/bin/python3 /path/to/porkbun_ddns.py /path/to/config.json /path/to/ip_cache.txt
```

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., every 5 minutes)
4. Set action to start the Python script with your config and cache file paths

### OPNsense Cron (Alternative Method)

If you prefer command-line cron setup on OPNsense instead of the web interface:

```bash
# Edit crontab directly
crontab -e

# Add this line for every 5 minutes (adjust as needed)
*/5 * * * * /usr/local/opnsense/scripts/dns/porkbun_ddns.py /usr/local/etc/porkbun-ddns.json /tmp/porkbun-ddns.cache
```

## Logging

The script uses rotating log files to prevent filesystem overflow, especially important on systems with limited `/tmp` space like OPNsense.

### Log Rotation Features

- **Automatic rotation**: When log file reaches maximum size (default: 1MB)
- **Backup retention**: Keeps a configurable number of backup files (default: 3)
- **Total storage limit**: With defaults, maximum ~4MB total log storage
- **Configurable**: Adjust log file location, size limits, and backup count

### Log Levels

- **INFO**: Normal operation messages (IP changes, DNS updates)
- **DEBUG**: Detailed operation information (use `--debug` flag)
- **ERROR**: Error conditions that prevent operation

### Log File Locations

- **Default**: `/tmp/porkbun.ddns.log` (with `.1`, `.2`, `.3` backups)
- **Custom**: Use `--log-file` parameter to specify alternative location
- **OPNsense recommendation**: Consider `/var/log/porkbun.ddns.log` for persistence across reboots

### Examples

```bash
# Default logging (1MB max, 3 backups, /tmp location)
python porkbun_ddns.py config.json cache.txt

# Custom log location and larger size limits
python porkbun_ddns.py config.json cache.txt --log-file /var/log/porkbun.ddns.log --log-max-size 5 --log-backup-count 2

# Minimal logging for space-constrained systems
python porkbun_ddns.py config.json cache.txt --log-max-size 0.5 --log-backup-count 1
```

## How It Works

1. **IP Detection**: Retrieves your current external IPv4 address from ifconfig.me
2. **Cache Check**: Compares current IP with cached IP to avoid unnecessary updates
3. **Record Management**: For each configured record:
   - Deletes existing A, ALIAS, and CNAME records
   - Creates new A record with current IP
4. **Caching**: Saves current IP to cache file for future comparisons

## Troubleshooting

### Common Issues

**"Error getting domain"**
- Verify your domain name is correct
- Ensure API access is enabled for the domain in your Porkbun account
- Check that your API credentials are valid

**"Failed to retrieve records"**
- Check your internet connection
- Verify API credentials
- Ensure Porkbun API is accessible

**IPv6 Issues**
- The script forces IPv4 detection to avoid IPv6 compatibility issues
- If you're still getting IPv6 addresses, check your system's DNS configuration

### Debug Mode

Run with `--debug` flag to see detailed operation logs:

```bash
python porkbun_ddns.py config.json ip_cache.txt --debug
```

## Frequently Asked Questions

### Why not use ddclient?

While ddclient supports Porkbun in general, **OPNsense's ddclient package doesn't include Porkbun support yet**. This tool fills that gap by providing:

- **Immediate Porkbun support** for OPNsense users
- **Native OPNsense integration** with configd service framework  
- **Purpose-built solution** while waiting for official ddclient package updates
- **Minimal dependencies** (just Python + requests)
- **Filesystem-safe logging** with automatic rotation

*Note: This tool bridges the gap until OPNsense's ddclient package potentially adds Porkbun support in future releases.*

### Why Porkbun?

Porkbun offers competitive domain pricing with free DNS management and a robust API - a cost-effective alternative to providers that charge premium rates for API access.

## Security Considerations

- Keep your `config.json` file secure and don't commit it to version control
- Use appropriate file permissions to protect your API credentials
- Consider using environment variables for sensitive data in production environments

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to Porkbun for providing a robust DNS API
- Thanks to ifconfig.me for reliable IP detection service
