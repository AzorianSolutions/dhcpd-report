#!/usr/bin/env python3
import csv
import os
import socket
import struct
import re
from isc_dhcp_leases import IscDhcpLeases
from loguru import logger
from pathlib import Path

# Data path containing configuration groups
data_path = Path(__file__).parent / 'data'

# Reports path to save reports to
reports_path = Path(__file__).parent / 'reports'

dhcp_range_regex = re.compile(r'range\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
config_groups = {}
lease_queue: dict[str, list] = {}
reports: dict[str, dict[str, list[int]]] = {}

# Load configuration groups
for config_group in os.listdir(data_path):
    config_groups[config_group] = {}
    for config in os.listdir(data_path / str(config_group)):
        config_path: Path = data_path / str(config_group) / str(config)
        with open(config_path) as f:
            config_groups[config_group][config] = (config_path, f.read())

for group_name in config_groups:
    group = config_groups[group_name]
    logger.info(f'Analyzing Group: {group_name}')

    if group_name not in lease_queue:
        lease_queue[str(group_name)] = []

    if group_name not in reports:
        reports[str(group_name)] = {}

    for config_name in group:
        config = group[config_name]

        if str(config_name).endswith('.leases'):
            logger.info(f'Leases file found: {config_name}')
            parser = IscDhcpLeases(config[0])
            leases = parser.get_current()

            logger.info(f'Found {len(leases)} leases in file.')

            lease_queue[str(group_name)].append(leases)
        else:
            logger.info(f'Config file found: {config_name}')
            matches = re.findall(dhcp_range_regex, config[1])

            if isinstance(matches, list):
                logger.info(f'Found {len(matches)} DHCP pools in config')

                for dhcp_range in matches:
                    range_key: str = dhcp_range[0] + '-' + dhcp_range[1]

                    if range_key not in reports[str(group_name)]:
                        range_start: int = struct.unpack("!L", socket.inet_aton(dhcp_range[0]))[0]
                        range_end: int = struct.unpack("!L", socket.inet_aton(dhcp_range[1]))[0]
                        reports[str(group_name)][range_key] = [0, range_start, range_end]

for group_name in lease_queue:
    for lease_list in lease_queue[group_name]:
        for lease in lease_list.values():
            logger.debug(f'Testing lease {lease.ip} in group {group_name}')

            ip: int = struct.unpack("!L", socket.inet_aton(lease.ip))[0]

            for report in reports[group_name].values():
                if ip >= report[1] and ip <= report[2]:
                    report[0] += 1

for group_name in reports:
    report_path = reports_path / str(group_name + '.csv')
    rows = [['Range Start', 'Range End', 'Total', 'Available', 'Used']]

    logger.info(f'Building group report for {group_name}...')

    for range_key in reports[group_name]:
        range_parts: list = range_key.split('-')
        range_start: str = range_parts[0]
        range_end: str = range_parts[1]
        ip_range: list = reports[group_name][range_key]
        lease_total: int = ip_range[2] - ip_range[1]
        lease_used: int = ip_range[0]
        lease_available: int = lease_total - lease_used
        rows.append([range_start, range_end, lease_total, lease_available, lease_used])

    logger.info(f'Saving group report for {group_name} to {report_path}')

    with open(report_path, 'w') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)
        f.close()
