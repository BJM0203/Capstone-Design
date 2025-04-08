import os

os.system("netsh wlan disconnect") # 초기 설정을 위해 연결되어있는 세션 종료
os.system("netsh wlan show network interface=Wi-Fi") # wifi 인터페이스 항목 출력
Selected_SSID = input('원하는 SSID 입력 : ')
try:
    os.system(f'''cmd /c "netsh wlan connect name=\"{Selected_SSID}\""''')
except:
    print("Error")