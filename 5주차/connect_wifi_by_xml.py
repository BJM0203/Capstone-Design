import os
os.system("netsh wlan show networks interface=Wi-Fi")
Selected_SSID = input('접속을 원하는 SSID 입력 : ')
Selected_PW = input('접속을 원하는 SSID 비밀번호 입력 : ')
config = """<?xml version=\"1.0\"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>"""+Selected_SSID+"""</name>
    <SSIDConfig>
        <SSID>
            <name>"""+Selected_SSID+"""</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>i
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>"""+Selected_PW+"""</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""

with open(Selected_SSID+".xml", "w") as file:
    file.write(config)
try:
    os.system("netsh wlan add profile filename=\"C:\\Users\\bjlov\\OneDrive\\바탕 화면\\visual stdio\\WirelessAP\\"+
              Selected_SSID+".xml\""+" interface=Wi-Fi")
    os.system("netsh wlan connect name=\""+Selected_SSID+"\" interface=Wi-Fi")
except:
    print("Error")