# Wi-Fi 연결 파일
import os
import subprocess

class WifiConnector:
    def __init__(self):
        self.networks = self.get_wifi_networks()
    
    def get_wifi_networks(self):
        # {"wifi1", "wifi2"..} 형식으로 딕셔너리 반환
        result = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True,
            text=True
        )
        
        ssid_auth_map = {}
        current_ssid = None
        
        for line in result.stdout.splitlines():
            line = line.strip()

            if line.startswith("SSID") and ":" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    ssid = parts[1].strip()
                    if ssid:
                        current_ssid = ssid
            
            elif "인증" in line and current_ssid:
                parts = line.split(":", 1)
                
                if len(parts) > 1:
                    auth = parts[1].strip()
                    ssid_auth_map[current_ssid] = auth
                    current_ssid = None
    
        return ssid_auth_map
    
    def choose_network(self):
        # ssid목록 보여주고 번호 선택
        if not self.networks:
            print("현재 감지되는 Wi-Fi가 없습니다.")
            return None

        ssids = list(self.networks.keys())
        print("감지된 Wi-Fi 목록 : ")
        for idx, ssid in enumerate(ssids, start=1):
            auth = self.networks[ssid]
            lock = "암호 O" if auth.lower() != "open" else "암호 X"
            print(f"[{idx}] {ssid} ({lock}, {auth})")
        
        while True:
            try:
                choice = int(input("연결할 Wi-Fi 번호를 선택하세요 : "))
                if 1 <= choice <= len(ssids):
                    selected_ssid = ssids[choice - 1]
                    auth = self.networks[selected_ssid]
                    return selected_ssid, auth
                else:
                    print("번호를 다시 확인하세요.")
            except ValueError:
                print("잘못된 입력 방식입니다. 숫자만 입력하세요.")
    
    def connect(self, ssid, password=None):
        # 프로파일 생성 및 연결
        print(f"'{ssid}' 연결 시도중...")
        
        # 프로파일 중복 SSID 충돌 방지위한 코드        
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
        
        subprocess.run(["netsh", "wlan", "add", "profile", f"filename={xml_file}"], capture_output=True, text=True)
        result = subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], capture_output=True, text=True)
        os.remove(xml_file)
        
        return True # 이 부분에 wifi 연결확인을 return해서 성공여부 확인.
''' 
    >> 인터넷 연결 확인 하는 코드라인
    >> ping, requests로 진행
    >> ping이 편하긴 하지만 requests가 더 정확함
    >> requests는 별도의 라이브러리 설치 및 공공wifi등 특수한 wifi 사용시 HTTP 리다이렉션이 301,302등 캡티브 포털? 
    >> 그런걸로 인증 및 로그인 필요로 해서 다른 코드가 올 수 있음. 

    def has_internet():
        1.
        result = subprocess.run(["ping", "-n", "1", "8.8.8.8"], capture_output=True, text=True)
        return "TTL=" in result.stdout
        
        2.
        response = requests.get("http://www.google.com", allow_redirects=False)
        if response.status_code == 200:
            print("정상적으로 연결됨")
        elif response.status_code in (301, 302):
            print("캡티브 포털에 가로막힘")
        else:
            print("인터넷 연결 실패")

'''
    
if __name__ == "__main__":
    connector = WifiConnector()
    selected = connector.choose_network()
        
    if selected:
        ssid, auth = selected
        if auth.lower() == "open":
            success = connector.connect(ssid)
        else:
            password = input(f"암호 O '{ssid}' 비밀번호를 입력하세요 : ")
            success = connector.connect(ssid, password)
                
        print("연결 성공!" if success else "연결 실패...")    
