import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

key = "babef8969e9c4d1884b50ea5e4fbee8"

guesses = [
    # Maint guesses
    "GnrlMaintBizPromtStus",
    "GnrlMaintBizPromtSttus",
    "GnrlMaintBizPrsgSttus",
    "GnrlMaintBizPromtStat",
    "GnrlMaintBizPrsgStat",
    "GenlMaintBizPromtStus",
    "GenlMaintBizPromtSttus",
    "GenlMaintBizPrsgSttus",
    
    # Refrm guesses
    "GnrlRefrmBussPromtStus",
    "GnrlRefrmBussPrsgSttus",
    "GenlRefrmBussPrsgSttus",
    "GnrlRefrmBussPromtSttus",
    "GenlRefrmBussPromtSttus",
    "GnrlRefrmSttus",
    "GenlRefrmSttus",
    "GnrlRefrmStus",
    "GenlRefrmStus",
    
    # MaintBiz guesses
    "GnrlMaintBizSttus",
    "GnrlMaintBizStus",
    "GenlMaintBizSttus",
    "GenlMaintBizStus",
    
    # Urban guesses
    "UrbnMaintBizPromtStus",
    "UrbnMaintBizPromtSttus",
    "UrbnRefrmBussPrsgSttus",
    
    # Other guesses
    "GnrlMaintSttus",
    "GnrlMaintStus",
    "RefrmBussPrsgSttus",
    "MaintBizPromtSttus"
]

for g in guesses:
    url = f"https://openapi.gg.go.kr/{g}"
    params = {
        "KEY": key,
        "Type": "json",
        "pIndex": 1,
        "pSize": 1
    }
    try:
        res = requests.get(url, params=params, verify=False, timeout=3)
        if "ERROR-310" not in res.text:
            print(f"\n[FOUND] Endpoint: {g} | Status: {res.status_code}")
            print(res.text[:1000])
        else:
            # print(".", end="", flush=True)
            pass
    except Exception as e:
        print(f"Error {g}: {e}")
