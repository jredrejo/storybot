#!/bin/bash
#
# WiFi Access Point Setup for StoryBot
#
# This script documents the setup process for the WiFi hotspot.
# StoryBot uses a TP-Link TL-WR802N access point for teacher mobile access.
#
# HARDWARE SETUP:
# 1. Connect TP-Link TL-WR802N to Jetson USB port or Ethernet
# 2. Power on the access point
# 3. Connect to the AP's default WiFi network (printed on device label)
# 4. Open browser to http://192.168.0.1 (default AP IP)
#
# MANUAL CONFIGURATION (Recommended):
#
# 1. Login to TP-Link admin panel (default admin/admin)
# 2. Navigate to Wireless > Wireless Settings
#    - Set SSID: "StoryBot"
#    - Set Region: your location
#    - Click Save
#
# 3. Navigate to Wireless > Wireless Security
#    - Set WPA/WPA2-Personal(PSK)
#    - Set Password: (use your secure password)
#    - Click Save
#
# 4. Navigate to DHCP > DHCP Settings
#    - Enable DHCP Server
#    - Set IP Pool: 192.168.0.100 - 192.168.0.200
#    - Set Lease Time: 120 minutes
#    - Click Save
#
# 5. Navigate to Network > LAN
#    - Set IP Address: 192.168.0.1 (if different)
#    - Set Subnet Mask: 255.255.255.0
#    - Click Save
#
# 6. Reboot the AP when prompted
#
# ALTERNATIVE: Using Jetson Built-in WiFi as AP
#
# NOTE: This is an alternative if you don't have the TP-Link AP.
# The TP-Link solution is preferred for stability and range.
#
# The following commands configure NetworkManager to use the Jetson's
# built-in WiFi as an access point. This requires WiFi hardware that
# supports AP mode (check with `iw list` for "AP" in supported interface modes).
#
set -e

AP_SSID="${AP_SSID:-StoryBot}"
AP_PASSWORD="${AP_PASSWORD}"
WLAN_INTERFACE="${WLAN_INTERFACE:-wlan0}"

echo "Configuring WiFi Access Point on $WLAN_INTERFACE"
echo "SSID: $AP_SSID"
echo "Password: $AP_PASSWORD"
echo ""
echo "WARNING: This will modify NetworkManager connections."
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# Check if interface exists
if ! ip link show "$WLAN_INTERFACE" &>/dev/null; then
    echo "ERROR: Interface $WLAN_INTERFACE not found"
    echo "Available interfaces:"
    ip link show | grep -E "^[0-9]+:" | awk '{print $2}' | sed 's/:$//'
    exit 1
fi

# Check if NetworkManager is available
if ! command -v nmcli &>/dev/null; then
    echo "ERROR: nmcli not found. Is NetworkManager installed?"
    exit 1
fi

# Check if AP mode is supported
if ! iw list 2>/dev/null | grep -q "^\s*Supported interface modes:" -A 10 | grep -q "^\s*\* AP"; then
    echo "WARNING: WiFi interface may not support AP mode"
    echo "Check with: iw list | grep -A 10 'Supported interface modes'"
    echo ""
    echo "Press Ctrl+C to cancel, or Enter to try anyway..."
    read
fi

# Delete existing connection if present
if nmcli connection show "$AP_SSID" &>/dev/null; then
    echo "Removing existing connection '$AP_SSID'"
    nmcli connection delete "$AP_SSID"
fi

# Create AP connection
echo "Creating access point connection..."
nmcli connection add \
    type wifi \
    ifname "$WLAN_INTERFACE" \
    con-name "$AP_SSID" \
    autoconnect yes \
    ssid "$AP_SSID"

# Configure AP mode
echo "Configuring AP mode and security..."
nmcli connection modify "$AP_SSID" \
    802-11-wireless.mode ap \
    802-11-wireless-security.key-mgmt wpa-psk \
    802-11-wireless-security.psk "$AP_PASSWORD" \
    ipv4.method shared \
    ipv4.addresses 192.168.12.1/24

# Start the connection
echo "Starting access point..."
nmcli connection up "$AP_SSID"

echo ""
echo "Access point configured successfully!"
echo ""
echo "SSID: $AP_SSID"
echo "Password: $AP_PASSWORD"
echo "IP Range: 192.168.12.0/24 (DHCP shared)"
echo ""
echo "Test with:"
echo "  nmcli connection show"
echo "  ip addr show $WLAN_INTERFACE"
echo ""
echo "To remove:"
echo "  nmcli connection delete $AP_SSID"
