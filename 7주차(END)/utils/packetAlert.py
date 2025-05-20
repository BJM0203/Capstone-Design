import socket
import subprocess
import re
from datetime import datetime
from win10toast import ToastNotifier
from scapy.all import sniff, ARP, DNS, IP
import requests

class PacketSniff:
    def __init__(self):
        self.my_ip = socket.gethostbyname(socket.gethostname())
        self.mac_table = {}
        self.notifier = ToastNotifier()

    def my_arp_table(self):
        self.mac_table = {}
        result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
        output = result.stdout

        for line in output.splitlines():
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F\-]{17})", line)
            if match:
                ip = match.group(1)
                mac = match.group(2).replace("-", ":").lower()
                self.mac_table[ip] = mac

    def alert(self, title, msg):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ALERT] {title} - {msg}")
        self.notifier.show_toast(title, msg, duration=5, threaded=True)
        subprocess.run(["netsh","wlan","disconnect"], capture_output=True, text=True)

    def handle_packet(self, pkt):
        # HTTPS 인증서 오류 및 리다이렉션 검사 (주석 해제 가능)
        # try:
        #     r = requests.get("https://www.google.com", timeout=5)
        #     if r.status_code in (301, 302):
        #         self.alert("HTTPS 리다이렉션", "캡티브 포털 또는 MITM 가능성")
        # except requests.exceptions.SSLError:
        #     self.alert("SSL 인증서 오류", "중간자 공격 의심")
        # except Exception:
        #     pass

        # ARP 감지
        if pkt.haslayer(ARP):
            print(f"ARP 패킷 감지: {pkt.summary()}")
            ip = pkt[ARP].psrc
            mac = pkt[ARP].hwsrc.lower()
            if ip in self.mac_table:
                if self.mac_table[ip] != mac:
                    self.alert("ARP 스푸핑 의심", f"{ip} → {mac} (이전: {self.mac_table[ip]})")
            else:
                self.mac_table[ip] = mac

        # DNS 감지
        elif pkt.haslayer(DNS) and pkt.haslayer(IP):
            if pkt[DNS].an:
                try:
                    qname = pkt[DNS].qd.qname.decode()
                    rdata = pkt[DNS].an.rdata
                    if str(rdata).startswith(("192.168.", "10.", "172.16.")):
                        self.alert("DNS 변조 의심", f"{qname} → {rdata}")
                except Exception:
                    pass
            

    def run(self):
        # print("[*] ARP 테이블 초기화 및 감시 시작...")
        # self.my_arp_table()
        # sniff(store=False, prn=self.handle_packet)
        print("--패킷 감시 시작--")
        try:
            sniff(iface="Wi-Fi", prn=self.handle_packet, store=0)
        except KeyboardInterrupt:
            print("\n 프로그램 종료.")

if __name__ == "__main__":
    ps = PacketSniff()
    ps.run()
