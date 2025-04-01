import os
import socket
import subprocess
import re
import json
import logging
from mac_vendor_lookup import MacLookup
from sshFRIEND.ssh_connector import ssh_connector, send_cmd


# Set up logging
logging.basicConfig(level=logging.INFO)


class NetworkOperations:
    def __init__(self, hostname, vlan_to_filter=None, username=None, password=None):
        """
        Initialize the NetworkOperations object with the hostname and optional filtering parameters.

        Args:
            hostname (str): The hostname of the network device.
            vlan_to_filter (int, optional): The VLAN ID to filter, if any. Defaults to None.
            username (str, optional): The SSH username for login. Defaults to None.
            password (str, optional): The SSH password for login. Defaults to None.
        """
        self.username, self.password = self.get_user_and_ssh_pass(username, password)
        self.hostname = hostname
        self.vlan_to_be_filtered = vlan_to_filter

    def get_user_and_ssh_pass(self, username, password):
        """
        Retrieve the SSH username and password, either from provided parameters or from the system.

        Args:
            username (str): The SSH username.
            password (str): The SSH password.

        Returns:
            tuple: A tuple containing the username and password.
        """
        if username and password:
            return username, password

        system_user = os.getenv("USER", "default_user")
        sshpass_file_path = os.path.expanduser("~/.sshpass")

        try:
            with open(sshpass_file_path, "r") as file:
                ssh_pass = file.read().strip()
        except FileNotFoundError:
            ssh_pass = "default_password"

        return system_user, ssh_pass

    def run_command(self, command):
        """
        Executes the provided SSH command and returns the output.
        """
        channel = ssh_connector(
            self.hostname, self.username, self.password, timeout=1200
        )
        return send_cmd(command, channel)

    def query_ipv6_dns(self, ipv6_address):
        """
        Perform an nslookup on an IPv6 address to retrieve the associated domain name.

        Args:
            ipv6_address (str): The IPv6 address to look up.

        Returns:
            str: The domain name associated with the given IPv6 address, or an error message if not found.
        """
        command = ["nslookup", ipv6_address]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            output_lines = result.stdout.splitlines()
            for line in output_lines:
                if "name =" in line:
                    domain_name = line.split("=")[1].strip().replace(".ip6.arpa.", "")
                    return domain_name
            return "Error: No domain name found."
        except subprocess.CalledProcessError as e:
            logging.error(f"Error performing nslookup: {e.stderr}")
            return f"Error: {e.stderr}"

    def perform_nslookup(self, domain_name):
        """
        Perform an nslookup on a domain name to resolve its IPv6 address.

        Args:
            domain_name (str): The Fully Qualified Domain Name (FQDN) to resolve.

        Returns:
            str: The resolved IPv6 address, or an error message if the resolution fails.
        """
        try:
            ipv6_addresses = [
                result[4][0]
                for result in socket.getaddrinfo(domain_name, None, socket.AF_INET6)
            ]
            return ipv6_addresses[0]
        except socket.gaierror as e:
            logging.error(f"Unable to resolve {domain_name}: {e}")
            return {"domain": domain_name, "error": f"Unable to resolve: {e}"}
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {"domain": domain_name, "error": f"Unexpected error: {e}"}

    def get_vendor(self, mac_address):
        """
        Fetch the vendor name for a given MAC address.

        Args:
            mac_address (str): The MAC address to look up.

        Returns:
            str: The name of the vendor, or 'unknown' if not found.
        """
        try:
            mac = MacLookup()
            return mac.lookup(mac_address)
        except Exception as e:
            logging.error(f"Error looking up MAC address {mac_address}: {e}")
            return "unknown"

    def process_mac_entry(self, fields, mac, vlan, port, vendor):
        """
        Helper function to process a single MAC entry, return the corresponding data.
        """
        ipv6 = self.mac_to_ipv6(mac=mac, olt_ipv6=self.hostname, vlan_id=vlan)
        return {
            "port": port,
            "vlan-id": vlan,
            "ipv6": ipv6,
            "device_name": self.query_ipv6_dns(ipv6),
            "vendor": vendor,
        }

    def get_arp_data(self):
        """
        Fetch ARP data and convert MAC addresses to IPv6 addresses.
        """
        channel = ssh_connector(
            self.hostname, self.username, self.password, timeout=1200
        )
        self.hostname = self.perform_nslookup(self.hostname)
        cmd_ = "show vlan bridge-port-fdb"
        output = self.run_command(cmd_)
        data_dict = {}

        if output:
            for line in output.splitlines():
                if line:
                    line = line.strip()
                    if line[:1].isnumeric() and "learned" in line:
                        stripped_line = line.split("learned")[0].strip()
                        fields = stripped_line.split()
                        if len(fields) == 4:
                            mac = fields[2]
                            vlan = fields[1]
                            port = fields[0]
                            vendor = self.get_vendor(mac)

                            if vlan and (
                                self.vlan_to_be_filtered is None
                                or int(vlan) == self.vlan_to_be_filtered
                            ):
                                if len(mac) > 5:
                                    data_dict[mac] = self.process_mac_entry(
                                        fields, mac, vlan, port, vendor
                                    )
        return data_dict

    def mac_to_ipv6(self, mac, vlan_id, olt_ipv6):
        """
        Converts a MAC address to an IPv6 address using the EUI-64 format.
        """
        parts = mac.split(":")
        first_byte = bin(int(parts[0], 16))[2:].zfill(8)
        flipped_first_byte = (
            first_byte[:6] + str(1 - int(first_byte[6])) + first_byte[7]
        )
        modified_mac = (
            "{:02x}".format(int(flipped_first_byte, 2))
            + ":"
            + ":".join(parts[1:3])
            + ":ff:fe:"
            + ":".join(parts[3:])
        )
        modified_mac = modified_mac.replace(":", "")
        a, b, c, d = (
            modified_mac[:4],
            modified_mac[4:8],
            modified_mac[8:12],
            modified_mac[12:],
        )
        new_mac = f"{a}:{b}:{c}:{d}"

        olt_ipv6 = olt_ipv6.split(":", 3)[:3]  # Split at the third colon
        olt_ipv6 = ":".join(olt_ipv6)

        return f"{olt_ipv6}:{vlan_id}:{new_mac}"

    def merge_data(self, base_data, additional_data, key_field):
        """
        Merges base data and additional data based on a common key field.
        """
        merged_data = {}
        for item in base_data:
            key_value = item[key_field]
            for k, v in additional_data.items():
                if key_value in v["port"]:
                    merged_data[k] = {**v, **item}
        return merged_data

    def make_pon_data(self, ont_pon_detail, mac_related_data):
        """
        Combine ONT details and MAC-related data to generate PON data.
        """
        return self.merge_data(ont_pon_detail, mac_related_data, "ont")

    def get_onts_pon_detail(self):
        """
        Retrieve detailed ONT (Optical Network Terminal) and PON (Passive Optical Network) information.
        """
        channel = ssh_connector(
            self.hostname, self.username, self.password, timeout=1200
        )
        commands = [
            "show equipment ont status pon detail",
            "show equipment ont status x-pon detail",
        ]
        results = {"pon": [], "x-pon": []}

        for cmd in commands:
            output = self.run_command(cmd)

            if output:
                if "pon" in cmd:
                    pattern = re.compile(
                        r"pon\s*"
                        r"-+\s*"
                        r"pon\s*:\s*(?P<pon>\S+)\s+ont\s*:\s*(?P<ont>\S+)\s+sernum\s*:\s*(?P<sernum>\S+)\s*"
                        r"admin-status\s*:\s*(?P<admin_status>\S+)\s+oper-status\s*:\s*(?P<oper_status>\S+)\s+olt-rx-sig-level\(dbm\)\s*:\s*(?P<olt_rx_sig_level>[-\d.]+)\s*"
                        r"ont-olt-distance\s*:\s*(?P<ont_olt_distance>[-\d.]+)\s+desc1\s*:\s*(?P<desc1>[^\n]+)\s*"
                        r"desc2\s*:\s*(?P<desc2>[^\n]+)\s*hostname\s*:\s*(?P<hostname>\S+)"
                    )
                elif "x-pon" in cmd:
                    pattern = re.compile(
                        r"x-pon\s*"
                        r"-+\s*"
                        r"x-pon\s*:\s*(?P<x_pon>\S+)\s+ont\s*:\s*(?P<ont>\S+)\s+sernum\s*:\s*(?P<sernum>\S+)\s*"
                        r"admin-status\s*:\s*(?P<admin_status>\S+)\s+oper-status\s*:\s*(?P<oper_status>\S+)\s+olt-rx-sig-level\(dbm\)\s*:\s*(?P<olt_rx_sig_level>[-\d.]+)\s*"
                        r"ont-olt-distance\s*:\s*(?P<ont_olt_distance>[-\d.]+)\s+desc1\s*:\s*(?P<desc1>[^\n]+)\s*"
                        r"desc2\s*:\s*(?P<desc2>[^\n]+)\s*hostname\s*:\s*(?P<hostname>\S+)"
                    )

                data = [match.groupdict() for match in pattern.finditer(output)]

                cleaned_data_list = [
                    {
                        key: (
                            value.replace("\r", "").strip()
                            if isinstance(value, str)
                            else value
                        )
                        for key, value in item.items()
                    }
                    for item in data
                ]

                if "pon" in cmd:
                    results["pon"].extend(cleaned_data_list)
                elif "x-pon" in cmd:
                    results["x-pon"].extend(cleaned_data_list)

        return results

    def get_all_devices(self):
        """
        Combine ONT details and MAC-related data to retrieve all devices and return them as a JSON string.
        """
        try:
            ont_data = self.get_onts_pon_detail()
            mac_related_data = self.get_arp_data()

            results = []
            for key in ["pon", "x-pon"]:
                if ont_data[key]:
                    results.append(self.make_pon_data(ont_data[key], mac_related_data))

            return json.dumps(results, indent=4)

        except Exception as e:
            logging.error(f"Error retrieving device data: {e}")
            return json.dumps(
                {"error": "An error occurred while retrieving device data."}, indent=4
            )


# HOW TO USE THIS PACKAGE
    #hostname = "nokia_olt_hostname_1"
    #network_operations = NetworkOperations(hostname, username="", password="",  vlan_to_filter=5)
    #results = network_operations.get_all_devices()
    #print(results)
