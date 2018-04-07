#!/bin/bash

modprobe tcp_ca_wrapper
modprobe tcp_bbr
modprobe tcp_veno
modprobe tcp_illinois
sysctl -w net.ipv4.tcp_congestion_control=tcp_ca_wrapper
