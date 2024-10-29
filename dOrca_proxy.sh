#!/bin/bash

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c() {
	echo "[+] Cleaning tun99 device"
	ip link delete tun99
	echo "[+] All done, bye!"
}

if [ "$EUID" -ne 0 ]
then
	echo "Please run as root"
	exit
elif [ "$#" -ne 2 ]
then
	echo "Usage: $0 CDIR Subnet (10.10.10.0/24) Proxy (socks5://127.0.0.1:1080)"
	exit
fi

net=$1
proxy=$2

# Create device tun99
ip tuntap add mode tun dev tun99

# Give addres to the new tun device
ip addr add 198.18.0.1/15 dev tun99

# Get the device up
ip link set dev tun99 up

# Route the desire ip range through the new device
ip route add $net via 198.18.0.1 dev tun99 metric 1

# Launch tun2socks

/usr/local/bin/tun2socks -device tun99 -proxy $proxy