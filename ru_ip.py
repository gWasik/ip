#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# version: 0.2

# importing the module
import ipaddress
from ipaddress import IPv4Address, IPv4Network, summarize_address_range, collapse_addresses
import re
import subprocess
import csv

# declaring the regex pattern for IP addresses
regexp_comment = re.compile(r'\s*#.*?')
regexp_iprange = re.compile(r'\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*-\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
regexp_network = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})')
regexp_ipv4 = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

# initializing the list object
excl_ips=[]
range_ips=[]
ru_ips=[]

# opening and reading the file
with open('/git/ip/russian_exclude.txt') as fh:
	ip_exclude = fh.readlines()

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
#print(f"excl_ips:{excl_ips}")

#remove dublicates from excluded list
range_ips.extend(excl_ips)
excl_ips.clear()
for ip in collapse_addresses(range_ips):
	excl_ips.extend(ip.subnets(new_prefix=32))
range_ips.clear()
#print(f"excl_ips:{excl_ips}")
#print(f"range_ips:{range_ips}")

#get russian networks from IP2LOCATION DB
with open('/git/ip/IP2LOCATION-LITE-DB1.CSV', newline='') as csvfile:
	ipreader = csv.reader(csvfile, delimiter=',', quotechar='"')
	for row in ipreader:
		#print(', '.join(row))
		#print(f"{row[0]} - {row[1]} : {row[2]}")
		if row[2]=='RU':
			ip_first = IPv4Address(int(row[0]))
			ip_last = IPv4Address(int(row[1]))
			ip_sum = summarize_address_range(ip_first, ip_last)
			ru_ips.extend(ip_sum)
			#break
#print(f"ru_ips:{ru_ips}")

#get russian networks from RIPN stat
with open('/git/ip/russian_include.txt') as fh:
	ip_raw = fh.readlines()
with open('/git/ip/russian_subnets_list_raw.txt') as fh:
	ip_raw = ip_raw + fh.readlines()

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

#intersect data from DBs
ru_ips.extend(range_ips)
range_ips.clear()
range_ips.extend(collapse_addresses(ru_ips))
ru_ips.clear()

#for info only
for ipaddr in range_ips:
	if ipaddr.is_unspecified:  print(f"is_unspecified:{str(ipaddr)}");
	if ipaddr.is_reserved: print(f"is_reserved:{str(ipaddr)}");
	if ipaddr.is_loopback: print(f"is_loopback:{str(ipaddr)}");
	if ipaddr.is_private: print(f"is_private:{str(ipaddr)}");
	if ipaddr.is_multicast: print(f"is_multicast:{str(ipaddr)}");
	if ipaddr.is_link_local: print(f"is_link_local:{str(ipaddr)}");

#exclude all ip from networks
for ip in excl_ips:
	b=0
	for network in range_ips:
		if network.supernet_of(ip):
			final_ips = network.address_exclude(ip)
			range_ips.extend(final_ips)
			range_ips.remove(network)
			#print(f"ip:{ip} removed from:{network}")
			b=1
	if b==0: print(f"ip:{ip} not found to remove!!!!!")

#final step
file_out = open("russian_subnets_list_processed.txt", "w+")

for ipaddr in collapse_addresses(range_ips):
	if ipaddr.is_unspecified: continue
	if ipaddr.is_loopback: continue
	if ipaddr.is_private: continue
	file_out.write(f"{str(ipaddr)}\n")

file_out.close()