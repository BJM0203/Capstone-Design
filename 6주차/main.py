from utils import WifiConnector, WifiSecEvaluator

def main():
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
        
        evaluator = WifiSecEvaluator(ssid, auth)
        level, report = evaluator.evaluate()

        print("\n[Wi-Fi 보안 평가 결과]")
        print(f"▶ SSID: {ssid}")
        # 여기 level 포트확인하는 메소드가 마지막으로 level을 저장해서 그 level으로 나오는 것 같아서 수정 필요함
        # 예를들어 보안,https,포트 3개를 보니깐 SSL 인증 안된다는 오류 제외하고 총 3개중 2,3개=위험/1개=주의/0개=안전 등으로 레벨 나눔
        print(f"▶ 보안 등급: {level}") 
        for line in report:
            print("  -", line)    


if __name__ == "__main__":
    main()
    