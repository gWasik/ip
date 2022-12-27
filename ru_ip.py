# -*- coding: utf-8 -*-

# importing the module
import ipaddress
from ipaddress import IPv4Address, IPv4Network, summarize_address_range, collapse_addresses
import re
import subprocess

# declaring the regex pattern for IP addresses
regexp_comment = re.compile(r'\s*#.*?')
regexp_iprange = re.compile(r'\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*-\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
regexp_network = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})')
regexp_ipv4 = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

# opening and reading the file
with open('/git/ip/russian_exclude.txt') as fh:
	ip_exclude = fh.readlines()

# initializing the list object
excl_ips=[]

# extracting the IP addresses
for line in ip_exclude:
	line=line.rstrip('\n')
	if regexp_comment.search(line):
		next
	elif regexp_iprange.search(line):
		ip_first = IPv4Address(regexp_iprange.search(line)[1])
		ip_last = IPv4Address(regexp_iprange.search(line)[2])
		ip_sum = summarize_address_range(ip_first, ip_last)
		excl_ips.extend(ip_sum)
	elif regexp_network.search(line):
		ip = IPv4Network(f"{line}")
		excl_ips.append(ip)
	elif regexp_ipv4.search(line):
		ip = IPv4Network(f"{line}/32")
		excl_ips.append(ip)
	else:
		digs = subprocess.run(['dig', '+short',line], stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
		for dig in digs:
			if regexp_ipv4.search(dig):
				ip = IPv4Network(f"{dig}/32")
				excl_ips.append(ip)
print(f"excl_ips:{excl_ips}")


with open('/git/ip/russian_include.txt') as fh:
	ip_raw = fh.readlines()
with open('/git/ip/russian_subnets_list_raw.txt') as fh:
	ip_raw = ip_raw + fh.readlines()

range_ips=[]

# extracting the IP addresses
for line in ip_raw:
	line=line.rstrip('\n')
	#print(f"raw ip:[{line}]")
	if regexp_comment.search(line):
		next
	elif regexp_iprange.search(line):
		ip_first = IPv4Address(regexp_iprange.search(line)[1])
		ip_last = IPv4Address(regexp_iprange.search(line)[2])
		ip_sum = summarize_address_range(ip_first, ip_last)
		range_ips.extend(ip_sum)
	elif regexp_network.search(line):
		ip = IPv4Network(regexp_network.search(line)[1])
		range_ips.append(ip)
	elif regexp_ipv4.search(line):
		ip = IPv4Network(f"{regexp_ipv4.search(line)[1]}/32")
		range_ips.append(ip)
	else:
		digs = subprocess.run(['dig', '+short',line], stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
		for dig in digs:
			if regexp_ipv4.search(dig):
				ip = IPv4Network(f"{dig}/32")
				range_ips.append(ip)
#print(f"range_ips:{range_ips}")

for ip in excl_ips:
	for network in range_ips:
		if ip.subnet_of(network):
			final_ips = network.address_exclude(ip)
			range_ips.extend(final_ips)
			range_ips.remove(network)
			next

file_out = open("russian_subnets_list_processed.txt", "w+")

for ipaddr in collapse_addresses(range_ips):
	file_out.write(f"{str(ipaddr)}\n")

file_out.close()