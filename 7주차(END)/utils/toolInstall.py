# 패키지 설치하는 파일
import subprocess
import sys # 현재 인터프리터 경로를 알아내는데 사용

def install_if_missing(package_name, import_name=None):
    try:
        if import_name is None:
            import_name = package_name
        __import__(import_name)
    except ImportError:
        try:
            print(f"'{package_name}' 설치 중...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"'{package_name}' 설치 완료")
        except subprocess.CalledProcessError as e:
            print(f"'{package_name}' 설치 실패! 에러: {e}")
            sys.exit(1)

# 설치 필요한 외부 라이브러리
def ensure_requirements():
    install_if_missing("requests")
    install_if_missing("psutil")
    install_if_missing("scapy")
    install_if_missing("win10toast")    




