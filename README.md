# Porkbun Dynamic DNS Client

A Python script to automatically update DNS records on Porkbun when your external IP address changes. Perfect for home servers, self-hosted services, or any scenario where you need to keep DNS records synchronized with a dynamic IP address.

## Features

- Automatic IP detection using ifconfig.me
- IP caching to avoid unnecessary API calls
- Support for multiple DNS records per domain
- Comprehensive logging with debug mode
- Manual IP override option
- IPv4 enforcement to prevent IPv6 issues
- Robust error handling and validation

## Prerequisites

- Python 3.6 or higher
- A Porkbun account with API access enabled
- API credentials from your Porkbun account

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/secretzer0/porkbun-ddns.git
   cd porkbun-ddns
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `config.json` file with your Porkbun API credentials and domain settings:

```json
{
    "apikey": "your_api_key_here",
    "secretapikey": "your_secret_api_key_here",
    "domain": "example.com",
    "records": [
        { "name": "www" },
        { "name": "home" },
        { "name": "@" }
    ]
}
```

### Configuration Options

- `apikey`: Your Porkbun API key
- `secretapikey`: Your Porkbun secret API key
- `domain`: The domain you want to update
- `records`: Array of DNS records to manage
  - `name`: The subdomain name (use "@" for the root domain)
- `endpoint` (optional): Custom API endpoint (defaults to Porkbun's v3 API)

### Getting API Credentials

1. Log into your Porkbun account
2. Go to Account → API Access
3. Enable API access for your domain
4. Generate your API key and secret key

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

# Show help
python porkbun_ddns.py --help
```

### Parameters

- `config`: Path to your configuration JSON file
- `cache`: Path to IP cache file (will be created if it doesn't exist)
- `-i, --ip`: Manually specify IP address instead of auto-detection
- `--debug`: Enable verbose debug logging

## Automation

### Cron Job (Linux/macOS)

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

## Logging

The script logs to both stdout and `/tmp/porkbun.ddns.log` (or equivalent temp directory on Windows). Use `--debug` flag for detailed logging.

### Log Levels

- **INFO**: Normal operation messages
- **DEBUG**: Detailed operation information (use `--debug` flag)
- **ERROR**: Error conditions that prevent operation

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
