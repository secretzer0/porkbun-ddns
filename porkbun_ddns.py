#!/usr/local/bin/python3

import json
import requests
import sys
import os
import argparse
import logging
from logging.handlers import RotatingFileHandler

def getRecords(domain, apiConfig):
    logging.debug(f"Fetching records for domain: {domain}")
    headers = {"Content-Type": "application/json"}
    response = requests.post(apiConfig["endpoint"] + '/dns/retrieve/' + domain, headers=headers, data=json.dumps(apiConfig))
    if not response.ok:
        logging.error(f"Failed to retrieve records. Status: {response.status_code}, Response: {response.text}")
        sys.exit(1)
    try:
        allRecords = response.json()
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON response from Porkbun: {e}, Raw response: {response.text}")
        sys.exit(1)
    if allRecords["status"] == "ERROR":
        logging.error("Error getting domain. Check to make sure you specified the correct domain, and that API access has been switched on for this domain.")
        sys.exit(1)
    return allRecords

def getMyIP(apiConfig):
    logging.debug("Retrieving external IPv4 from ifconfig.me")
    try:
        import socket
        from requests.packages.urllib3.util.connection import allowed_gai_family

        # Force IPv4 for the request
        def force_ipv4():
            return socket.AF_INET

        requests.packages.urllib3.util.connection.allowed_gai_family = force_ipv4

        response = requests.get("https://ifconfig.me/all.json", headers={"User-Agent": "vyzonDDNS", "Accept": "application/json"}, timeout=10)
        if not response.ok:
            logging.error(f"Failed to fetch IP. Status: {response.status_code}, Response: {response.text}")
            sys.exit(1)
        data = response.json()
        ip_addr = data.get("ip_addr", "")
        if ":" in ip_addr:
            logging.error(f"Got IPv6 address ({ip_addr}) despite forcing IPv4. Check system settings or DNS resolution behavior.")
            sys.exit(1)
        return ip_addr
    except Exception as e:
        logging.error(f"Exception while retrieving IP: {e}")
        sys.exit(1)

def deleteRecord(apiConfig, domain, fqdn):
    logging.debug(f"Attempting to delete existing records for {fqdn}")
    for i in getRecords(domain, apiConfig)["records"]:
        if i["name"] == fqdn and i["type"] in ('A', 'ALIAS', 'CNAME'):
            logging.debug(f"Deleting record ID {i['id']} of type {i['type']}")
            _ = json.loads(requests.post(apiConfig["endpoint"] + '/dns/delete/' + domain + '/' + i["id"], data=json.dumps(apiConfig)).text)

def createRecord(apiConfig, domain, subDomain, myIP):
    createObj = apiConfig.copy()
    createObj.update({'name': subDomain, 'type': 'A', 'content': myIP, 'ttl': 300})
    logging.debug(f"Creating new A record for {subDomain}.{domain} with IP {myIP}")
    create = json.loads(requests.post(apiConfig["endpoint"] + '/dns/create/' + domain, data=json.dumps(createObj)).text)
    return create

def load_cached_ip(cache_file):
    logging.debug(f"Loading cached IP from {cache_file}")
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return f.read().strip()
    return None

def save_cached_ip(cache_file, ip):
    logging.debug(f"Saving current IP {ip} to cache file {cache_file}")
    with open(cache_file, 'w') as f:
        f.write(ip)

def main():
    parser = argparse.ArgumentParser(
        description="Porkbun Dynamic DNS client",
        epilog="""
Example config.json:

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
""",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("config", help="Path to config.json with API keys, domain, and records list")
    parser.add_argument("cache", help="Path to IP cache file")
    parser.add_argument("-i", "--ip", help="Specify IP manually (optional)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--log-file", default="/tmp/porkbun.ddns.log", help="Log file path (default: /tmp/porkbun.ddns.log)")
    parser.add_argument("--log-max-size", type=int, default=1, help="Max log file size in MB (default: 1)")
    parser.add_argument("--log-backup-count", type=int, default=3, help="Number of backup log files to keep (default: 3)")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # Logging configuration with rotation to prevent filesystem overflow
    log_level = logging.DEBUG if args.debug else logging.INFO
    log_format = '%(asctime)s [%(levelname)s] %(message)s'

    logging.getLogger().setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))

    # Rotating file handler - configurable size and backup count
    # This prevents filesystem overflow by limiting total log storage
    log_file = args.log_file
    max_bytes = args.log_max_size * 1024 * 1024  # Convert MB to bytes
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=max_bytes,
        backupCount=args.log_backup_count
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format))

    logging.getLogger().addHandler(console_handler)
    logging.getLogger().addHandler(file_handler)

    with open(args.config, "r") as f:
        config = json.load(f)

    apiConfig = {
        "apikey": config["apikey"],
        "secretapikey": config["secretapikey"],
        "endpoint": config.get("endpoint", "https://api-ipv4.porkbun.com/api/json/v3")
    }
    domain = config["domain"]
    records = config["records"]

    if args.ip:
        myIP = args.ip
        logging.debug(f"Using manually specified IP: {myIP}")
    else:
        myIP = getMyIP(apiConfig)
        logging.debug(f"Auto-detected external IP: {myIP}")

    cached_ip = load_cached_ip(args.cache)
    if cached_ip == myIP:
        logging.info(f"IP unchanged ({myIP}), no update needed.")
        return

    logging.info(f"IP has changed or first run. Old: {cached_ip}, New: {myIP}")

    for record in records:
        name = record["name"]
        fqdn = name if name == "@" else f"{name}.{domain}"
        deleteRecord(apiConfig, domain, fqdn)
        result = createRecord(apiConfig, domain, name, myIP)
        logging.info(f"{fqdn}: {result['status']}")

    save_cached_ip(args.cache, myIP)

if __name__ == "__main__":
    main()
