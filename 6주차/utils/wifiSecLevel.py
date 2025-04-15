# wifi 연결 시 wifi 안정성 표시
import requests
import socket
import psutil
import subprocess
import sys

# 보안기관에서 공격에 악용되거나 필요하지 않다면 막는 것을 권장하는 프로토콜 포트 번호들
RISKY_TCP_PORTS = [20, 21, 22, 23, 25, 80, 110, 135, 139, 143, 445, 1433, 3389]

class WifiSecEvaluator:
    def __init__(self, ssid, auth_method):
        self.ssid = ssid
        self.auth_method = auth_method
        self.level = "분석 중..."       
        self.report = []

    # 암호 여부 학인
    def evaluate_encryption(self):
        auth = self.auth_method.lower()
        if "open" in auth or "wep" in auth:
            self.level = "위험"
            self.report.append("암호화 미적용 또는 WEP - 매우 위험")
        elif "wpa" in auth and "2" not in auth:
            self.level = "주의"
            self.report.append("WPA - 보안 낮음")
        elif "wpa2" in auth or "wpa3" in auth:
            self.report.append("WPA2 이상 - 보안 양호")
        else:
            self.level = "주의"
            self.report.append("인증 방식 불명확")
    
    # HTTP code 확인
    def evaluate_https(self):
        try:
            r = requests.get("https://www.google.com", allow_redirects=False, timeout=5)
            if r.status_code in (301, 302):
                self.level = "주의"
                self.report.append("HTTPS 리다이렉션 감지 - 포털 가능성")
            elif r.status_code == 200:
                self.report.append("HTTPS 응답 정상")
            else:
                self.report.append(f"예기치 않은 응답 코드: {r.status_code}")
        except requests.exceptions.SSLError:
            self.level = "위험"
            self.report.append("SSL 인증서 오류 - 중간자 공격(MITM) 가능성 있음")
            # print("-- 연결종료 --")
            # subprocess.run(["netsh", "wlan", "disconnect"], capture_output=True, text=True)
            # sys.exit(1)
        except Exception as e:
            self.report.append(f"HTTPS 요청 실패: {e}")
            
    # 열려있는 포트 스캔
    def evaluate_ports(self):
        ip = self.get_gateway_ip()
        if not ip:
            self.report.append("게이트웨이 IP 확인 실패")
            return

        open_ports = []
        for port in RISKY_TCP_PORTS:
            # ~~(IPv4주소만 사용, TCP 연결 사용) => 일반 웹, SSH, FTP등 통신에 사용
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            try:
                s.connect((ip, port))
                open_ports.append(port)
            except:
                pass
            finally:
                s.close()

        if open_ports:
            self.level = "주의"
            self.report.append(f"위험 포트 열려 있음: {open_ports}")
        else:
            self.report.append("위험 포트 열림 없음")

    # 라우터(게이트웨이)IP 주소 추출 -> 라우터 방향으로 포트 스캔을 하기 위함
    def get_gateway_ip(self):
        # psutil : 네트워크 인터페이스의 모든 정보 알려줌
        # .net~ : 컴퓨터에 있는 모드 네트워크 인터페이스의 주소 반환 후 .values로 주소 목록만 순회
        for interfaces in psutil.net_if_addrs().values():
            for snic in interfaces:
                # and 전 :IPv4 주소만 검색 / and 후 : DHCP 실패시 할당되는 임시 IP
                if snic.family == socket.AF_INET and not snic.address.startswith("169.254"): 
                    return snic.address
        return None

    def evaluate(self):
        self.evaluate_encryption()
        self.evaluate_https()
        self.evaluate_ports()
        return self.level, self.report
