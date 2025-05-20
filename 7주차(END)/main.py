from utils import WifiConnector, WifiSecEvaluator, PacketSniff
from scapy.all import sniff
import subprocess

def main():
    # -Wi-FI 연결
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
            
        if success:
            print("<<연결 성공!>>")
        else:
            print("<<연결 실패...>>")
            exit(1)
        #print("<<연결 성공!>>" if success else "<<연결 실패...>>" exit(1))
        
        evaluator = WifiSecEvaluator(ssid, auth)
        level, report = evaluator.evaluate()

        print("\n[Wi-Fi 보안 평가 결과]")
        print(f"▶ SSID: {ssid}") 
        for line in report:
            print("  -", line)    
    
    # -패킷 감지
    ps = PacketSniff()
    ps.run()


if __name__ == "__main__":
    subprocess.run(["netsh","wlan","dissconnect"], capture_output=True, text=True) # debug
    main()
    