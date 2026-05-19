import requests
import json
import urllib.parse

class OnbidAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://apis.data.go.kr/B551505/kamcoPblsalThingInqireSvc/getKamcoPblsalThingDtls"
        self.list_url = "http://apis.data.go.kr/B551505/kamcoPblsalThingInqireSvc/getKamcoPblsalThingList"

    def _request(self, url, params):
        try:
            # API Key is passed as-is in the query string to avoid double-encoding issues
            query_string = f"?serviceKey={self.api_key}"
            for k, v in params.items():
                query_string += f"&{k}={v}"
            
            full_url = url + query_string
            print(f"Requesting Onbid API: {full_url}")
            
            response = requests.get(full_url, timeout=15)
            
            if response.status_code == 200:
                # We expect JSON, but data.go.kr often returns XML by default.
                # If the API allows &type=json, we can append it.
                return {"success": True, "data": response.text}
            else:
                return {"success": False, "error": f"API Error {response.status_code}: {response.text[:200]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_property_details(self, management_number: str):
        """물건관리번호로 공매 물건 상세 정보를 조회합니다."""
        # 공공데이터포털은 종종 하이픈을 제거한 번호를 요구합니다.
        clean_num = management_number.replace("-", "")
        params = {
            "pageNo": 1,
            "numOfRows": 10,
            "cltrMngNo": clean_num,
            "type": "json" # json 포맷 요청 (API 지원 시)
        }
        return self._request(self.base_url, params)

    def get_property_list(self, management_number: str):
        """물건 목록 조회 API (상세 조회가 안 될 경우 폴백)"""
        clean_num = management_number.replace("-", "")
        params = {
            "pageNo": 1,
            "numOfRows": 10,
            "cltrMngNo": clean_num,
            "type": "json"
        }
        return self._request(self.list_url, params)

if __name__ == "__main__":
    import sys
    # 사용자가 제공한 API Key
    TEST_API_KEY = "f3a15815abecaa938c1aae6a9a9a792bb32efd06c2af0be789a7aae0d92eb9f9"
    client = OnbidAPIClient(TEST_API_KEY)
    
    num = sys.argv[1] if len(sys.argv) > 1 else "2026-0400-023211"
    print(f"Testing Onbid API for management number: {num}")
    result = client.get_property_details(num)
    print("Result:", result)
