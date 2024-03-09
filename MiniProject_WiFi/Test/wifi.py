import win32api
import win32net
import win32_network

def scan_wifi_networks():
    wlan_interfaces = win32_network.WlanOpenHandle()
    if not wlan_interfaces:
        return []

    networks = []
    query_result = win32_network.WlanQueryInterface(wlan_interfaces, win32_network.WlanInterfaceGuid, win32_network.wlan_intf_opcode_current_network_list)
    if query_result:
        for network in query_result[1]:
            networks.append({
                'ssid': network.get('dot11Ssid', {}).get('SSID', ''),
                'bssid': ':'.join('%02X' % b for b in network.get('dot11Bssid', [0])),
                'signal': network.get('rssi', 0),
                'channel': network.get('dot11Channel', {}).get('ChannelFrequency', 0),
                'security': get_security(network.get('dot11DefaultAuthAlgorithm', 0))
            })

    win32_network.WlanCloseHandle(wlan_interfaces)

    return networks

def get_security(security):
    if security == win32net.dot11_auth_algorithm_open:
        return 'Open'
    elif security == win32net.dot11_auth_algorithm_shared_key:
        return 'WEP'
    elif security == win32net.dot11_auth_algorithm_wpa:
        return 'WPA'
    elif security == win32net.dot11_auth_algorithm_wpa2:
        return 'WPA2'
    elif security == win32net.dot11_auth_algorithm_wpa_psk:
        return 'WPA-PSK'
    elif security == win32net.dot11_auth_algorithm_wpa2_psk:
        return 'WPA2-PSK'
    else:
        return 'Unknown'

def main():
    networks = scan_wifi_networks()
    print('SSID\t\t\t\t\tBSSID\t\t\t\t\tSignal\tChannel\tSecurity')
    print('--------------------------------------------------------------------------------------------------')
    for network in networks:
        print(f"{network['ssid']}\t{network['bssid']}\t{network['signal']}\t{network['channel']}\t{network['security']}")

if __name__ == "__main__":
    main()