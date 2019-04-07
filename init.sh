#!/bin/bash

# Init wrapper
# Attach required CA to wrapper
# Set wrapper as default

modprobe tcp_ca_wrapper
modprobe tcp_vegas
modprobe tcp_westwood
modprobe tcp_illinois
modprobe tcp_cubic
modprobe tcp_bbr
sysctl -w net.ipv4.tcp_congestion_control=tcp_ca_wrapper
