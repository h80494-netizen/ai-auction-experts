import sys
import os

# Include backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sgis_service import sgis_service

print("Testing SGIS Authentication...")
token = sgis_service.get_access_token()
print("Token:", token)

if token:
    print("Authentication Successful!")
    # Test coordinates in Seoul (e.g., Gangnam Station)
    lat, lng = 37.4979, 127.0276
    x, y = sgis_service.transform_coords(lat, lng)
    print(f"Transformed GPS ({lat}, {lng}) to UTM-K: X={x:.2f}, Y={y:.2f}")
    
    print("Fetching Demographics within 1km circle...")
    data = sgis_service.fetch_demographics_1km(lat, lng)
    print("Result data:")
    import pprint
    pprint.pprint(data)
else:
    print("Authentication Failed!")
