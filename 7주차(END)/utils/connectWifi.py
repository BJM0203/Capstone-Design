import os
import subprocess

class WifiConnector:
    def __init__(self):
        # networks: { ssid: {"auth": auth, "bssids": set()} }
        self.networks = self.get_wifi_networks()
    
    def get_wifi_networks(self):
        result = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True,
            text=True
        )
        
        networks = {}
        current_ssid = None
        current_auth = None
        
        for line in result.stdout.splitlines():
            line = line.strip()
            # SSID
            if line.startswith("SSID") and ":" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    ssid = parts[1].strip()
                    if ssid:
                        current_ssid = ssid
                        if current_ssid not in networks:
                            networks[current_ssid] = {"auth": None, "bssids": set()}
            
            # 인증 방식
            elif "인증" in line and current_ssid:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    auth = parts[1].strip()
                    networks[current_ssid]["auth"] = auth
                    current_auth = auth
            
            # BSSID 정보 추출
            elif line.startswith("BSSID") and ":" in line and current_ssid:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    bssid = parts[1].strip()
                    # 윈도우는 BSSID 번호까지 나오므로, "BSSID 1 : xx:xx:xx:xx:xx:xx"형식인 경우를 처리
                    # bssid가 "1 xx:xx:xx:xx:xx:xx" 형태일 수 있음 -> 마지막 17글자 MAC주소 추출
                    if len(bssid) > 17:
                        bssid = bssid[-17:]
                    networks[current_ssid]["bssids"].add(bssid)
        
        return networks
    
    def detect_fake_ap(self):
        print("\n=== Fake AP 탐지 결과 ===")
        found_fake = False
        device1 = ""
        device2 = ""
        other_devices = []
        for ssid, info in self.networks.items():
            bssids = info["bssids"]
            if bssids:
                tmp = next(iter(bssids))
                device1 = ":".join(tmp.split(":")[:3])
                devcie2 = ":".join(tmp.split(":")[:4])
                #print(device1)
                #print(device2)
            else:
                print("{ssid}의 bssids가 비어있습니다.")
                exit(1)
            for bsid in bssids:
                mac = ":".join(tmp.split(":")[:3])
                if mac != device1:
                    other_device = mac
            if len(bssids) > 1 and len(other_devices) > 1:
                found_fake = True
                print(f"[!] 의심 SSID '{ssid}' 가 여러 BSSID로 탐지됨:")
                for other_device in other_devices:
                    print(f"    - {other_device}")
        if not found_fake:
            print("의심되는 Fake AP가 발견되지 않았습니다.")
        print("=========================\n")
    
    def choose_network(self):
        if not self.networks:
            print("현재 감지되는 Wi-Fi가 없습니다.")
            return None

        ssids = list(self.networks.keys())
        print("감지된 Wi-Fi 목록 : ")
        for idx, ssid in enumerate(ssids, start=1):
            auth = self.networks[ssid]["auth"]
            lock = "암호 X" if auth.lower() == "오픈" or auth.lower() == "open" else "암호 O"
            print(f"[{idx}] {ssid} ({lock}, {auth})")
        
        while True:
            try:
                choice = int(input("연결할 Wi-Fi 번호를 선택하세요 : "))
                if 1 <= choice <= len(ssids):
                    selected_ssid = ssids[choice - 1]
                    auth = self.networks[selected_ssid]["auth"]
                    return selected_ssid, auth
                else:
                    print("번호를 다시 확인하세요.")
            except ValueError:
                print("잘못된 입력 방식입니다. 숫자만 입력하세요.")
    
    def connect(self, ssid, password=None):
        print(f"'{ssid}' 연결 시도중...")
        
        subprocess.run(["netsh", "wlan", "delete", "profile", f"name={ssid}"], capture_output=True, text=True)

        if password:
            wifi_profile=f"""
            <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
            <name>{ssid}</name>
            <SSIDConfig>
                <SSID>
                    <name>{ssid}</name>
                </SSID>
            </SSIDConfig>
            <connectionType>ESS</connectionType>
            <connectionMode>auto</connectionMode>
            <MSM>
                <security>
                    <authEncryption>
                        <authentication>WPA2PSK</authentication>
                        <encryption>AES</encryption>
                        <useOneX>false</useOneX>
                    </authEncryption>
                    <sharedKey>
                        <keyType>passPhrase</keyType>
                        <protected>false</protected>
                        <keyMaterial>{password}</keyMaterial>
                    </sharedKey>
                </security>
            </MSM>
        </WLANProfile>
        """
        else:
            wifi_profile=f"""
            <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
            <name>{ssid}</name>
            <SSIDConfig>
                <SSID>
                    <name>{ssid}</name>
                </SSID>
            </SSIDConfig>
            <connectionType>ESS</connectionType>
            <connectionMode>auto</connectionMode>
            <MSM>
                <security>
                    <authEncryption>
                        <authentication>open</authentication>
                        <encryption>none</encryption>
                        <useOneX>false</useOneX>
                    </authEncryption>
                </security>
            </MSM>
        </WLANProfile>
        """
        
        xml_file = f"{ssid}.xml"
        with open(xml_file, "w") as file:
            file.write(wifi_profile)
        
        import time
        time.sleep(2)
        
        profile_result = subprocess.run(["netsh", "wlan", "add", "profile", f"filename={xml_file}"], capture_output=True, text=True)
        print("프로파일 추가 결과 : ", profile_result.stdout.strip())
        if profile_result.stderr:
            print("에러:", profile_result.stderr.strip())
            exit(1)
            
        result = subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], capture_output=True, text=True)
        os.remove(xml_file)
        
        # 연결 성공 여부 판단 (간단히 결과 출력에서 성공 단어 확인)
        #print(result.returncode)
        if result.returncode == 0:
            return True
        else:
            return False

if __name__ == "__main__":
    connector = WifiConnector()
    connector.detect_fake_ap()  # Fake AP 탐지 먼저 실행
    selected = connector.choose_network()
    if selected:
        ssid, auth = selected
        if auth.lower() == "오픈":
            success = connector.connect(ssid)
        else:
            password = input(f"암호 O '{ssid}' 비밀번호를 입력하세요 : ")
            success = connector.connect(ssid, password)
                
        print("연결 성공!" if success else "연결 실패...")
