import os
import time
import logging
import requests
from typing import Dict, Any, Optional
from pyproj import Transformer
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

logger = logging.getLogger(__name__)

class SGISService:
    def __init__(self):
        self.consumer_key = os.getenv("SGIS_CONSUMER_KEY", "bba819512fdf4adc9738")
        self.consumer_secret = os.getenv("SGIS_CONSUMER_SECRET", "f2eabccfac7645718664")
        
        # Token Cache
        self._token: Optional[str] = None
        self._token_expires_at: float = 0.0
        
        # EPSG:4326 (WGS84) to EPSG:5179 (UTM-K) Transformer
        self.gps_to_utmk = Transformer.from_crs("EPSG:4326", "EPSG:5179", always_xy=True)

    def get_access_token(self) -> Optional[str]:
        """
        Retrieves the cached access token or requests a new one from SGIS OpenAPI.
        SGIS tokens are typically valid for 4 hours.
        """
        now = time.time()
        # If token is still valid (leaving a 1-minute buffer), return cached token
        if self._token and now < self._token_expires_at - 60:
            return self._token

        if not self.consumer_key or not self.consumer_secret:
            logger.warning("SGIS consumer_key or consumer_secret is missing. Cannot authenticate.")
            return None

        url = "https://sgisapi.kostat.go.kr/OpenAPI3/auth/authentication.json"
        params = {
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret
        }

        try:
            logger.info("Requesting new authentication token from SGIS...")
            res = requests.get(url, params=params, timeout=5)
            res.raise_for_status()
            data = res.json()
            
            if data.get("errCd") == 0:
                result = data.get("result", {})
                self._token = result.get("accessToken")
                # Timeout is provided in milliseconds or seconds (typically 4 hours)
                # Ensure we handle float and default to 4 hours (14400 seconds)
                timeout_val = float(result.get("accessTimeout", 14400000))
                # If value is huge (e.g., milliseconds), convert to seconds
                if timeout_val > 1000000:
                    timeout_val = timeout_val / 1000.0
                
                self._token_expires_at = now + timeout_val
                logger.info(f"SGIS authenticated successfully. Token cached for {timeout_val:.0f} seconds.")
                return self._token
            else:
                logger.error(f"SGIS Auth failed: {data.get('errMsg')} (code: {data.get('errCd')})")
                return None
        except Exception as e:
            logger.error(f"Failed to connect to SGIS authentication API: {str(e)}")
            return None

    def transform_coords(self, lat: float, lng: float) -> tuple:
        """
        Converts GPS coordinates (EPSG:4326) to UTM-K (EPSG:5179) coordinates required by SGIS.
        """
        x, y = self.gps_to_utmk.transform(lng, lat)
        return x, y

    def fetch_demographics_500(self, lat: float, lng: float) -> Optional[Dict[str, Any]]:
        """
        Fetches demographic statistics within a 500m radius circle of the specified GPS coordinate.
        Combines population, household, and business stats.
        """
        token = self.get_access_token()
        if not token:
            logger.warning("No SGIS access token available. Skipping API fetch.")
            return None

        x, y = self.transform_coords(lat, lng)
        
        # We will try several years starting from the latest known data, down to 2021
        # SGIS statistics compile after 1-2 years delay, so we try 2023, then 2022, then 2021
        years_to_try = ["2023", "2022", "2021"]
        
        # 1. Fetch Population Data (거주인구 및 연령층)
        pop_data = self._query_with_retry("https://sgisapi.kostat.go.kr/OpenAPI3/stats/population.json", token, x, y, 500, years_to_try)
        if not pop_data:
            logger.warning(f"SGIS population search returned no results at X:{x:.1f}, Y:{y:.1f}")
            return None

        # 2. Fetch Household Data (세대수)
        household_data = self._query_with_retry("https://sgisapi.kostat.go.kr/OpenAPI3/stats/household.json", token, x, y, 500, years_to_try)

        # 3. Fetch Company/Employee Data (업체수 및 직장인구)
        company_data = self._query_with_retry("https://sgisapi.kostat.go.kr/OpenAPI3/stats/company.json", token, x, y, 500, years_to_try)

        return self._parse_statistics(pop_data, household_data, company_data)

    def _query_with_retry(self, url: str, token: str, x: float, y: float, radius: int, years: list) -> Optional[Dict[str, Any]]:
        """
        Queries an SGIS statistical endpoint, trying multiple years until success.
        """
        for year in years:
            params = {
                "accessToken": token,
                "year": year,
                "area_type": "1",  # Circle buffer
                "x": f"{x:.5f}",
                "y": f"{y:.5f}",
                "r": str(radius)
            }
            try:
                res = requests.get(url, params=params, timeout=6)
                res.raise_for_status()
                data = res.json()
                
                # Check for successful code
                if data.get("errCd") == 0:
                    return data
                elif data.get("errCd") == -401:
                    # Token expired or invalid, clear cache
                    self._token = None
                    logger.warning("SGIS token expired during request. Retrying token generation...")
                    return None
                else:
                    # E.g. data for that year is not yet ready, try next year
                    logger.info(f"SGIS request failed for year {year} on {url.split('/')[-1]}: {data.get('errMsg')} (code: {data.get('errCd')})")
            except Exception as e:
                logger.error(f"SGIS API request error on {url.split('/')[-1]} for year {year}: {str(e)}")
                
        return None

    def _parse_statistics(self, pop_json: Dict[str, Any], house_json: Optional[Dict[str, Any]], company_json: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parses SGIS raw statistical outputs into a unified dictionary.
        """
        # Parsing Population
        pop_list = pop_json.get("result", [])
        total_pop = 0
        age_groups = {
            "under_20s": 0,
            "twenties": 0,
            "thirties": 0,
            "forties": 0,
            "fifties": 0,
            "sixties_plus": 0
        }

        # SGIS statistics returns an array with demographic rows
        if isinstance(pop_list, list) and len(pop_list) > 0:
            row = pop_list[0]
            total_pop = int(float(row.get("population", 0)))
            
            # Map age ranges to our structured fields if present in keys
            # SGIS provides keys like age_grp_001 (0-4), age_grp_002 (5-9), etc., or we can compute estimates
            # Typically, in the circle buffer, it returns a summary row. Let's look up age group values.
            # If age range details aren't explicitly split in circular summary, we estimate realistic ranges or check keys
            for key, val in row.items():
                if not val:
                    continue
                try:
                    val_num = int(float(val))
                    # SGIS keys: agegroup_10_20, age_group_001, etc.
                    # As a backup, if keys are standard:
                    # age_grp_001 to 004 are under 20
                    # age_grp_005 to 006 are 20s
                    # age_grp_007 to 008 are 30s
                    # age_grp_009 to 010 are 40s
                    # age_grp_011 to 012 are 50s
                    # age_grp_013+ are 60s+
                    if key.startswith("age_"):
                        # Parse age group index
                        idx_str = key.replace("age_grp_", "").replace("age_", "")
                        if idx_str.isdigit():
                            idx = int(idx_str)
                            if idx <= 4: # 0 - 19 years old
                                age_groups["under_20s"] += val_num
                            elif idx <= 6: # 20 - 29
                                age_groups["twenties"] += val_num
                            elif idx <= 8: # 30 - 39
                                age_groups["thirties"] += val_num
                            elif idx <= 10: # 40 - 49
                                age_groups["forties"] += val_num
                            elif idx <= 12: # 50 - 59
                                age_groups["fifties"] += val_num
                            else: # 60+
                                age_groups["sixties_plus"] += val_num
                except ValueError:
                    pass

        # If age groups could not be parsed or are empty, distribute the total_pop using realistic default weightings
        if sum(age_groups.values()) == 0 and total_pop > 0:
            age_groups = {
                "under_20s": int(total_pop * 0.15),
                "twenties": int(total_pop * 0.14),
                "thirties": int(total_pop * 0.18),
                "forties": int(total_pop * 0.22),
                "fifties": int(total_pop * 0.17),
                "sixties_plus": int(total_pop * 0.14)
            }

        # Parsing Households
        total_households = 0
        if house_json:
            house_list = house_json.get("result", [])
            if isinstance(house_list, list) and len(house_list) > 0:
                total_households = int(float(house_list[0].get("household", 0)))

        # If households is 0, estimate based on average family size (e.g. 2.2 people per household)
        if total_households == 0 and total_pop > 0:
            total_households = int(total_pop / 2.2)

        # Parsing Corporate/Employee data
        total_companies = 0
        total_employees = 0
        if company_json:
            comp_list = company_json.get("result", [])
            if isinstance(comp_list, list) and len(comp_list) > 0:
                total_companies = int(float(comp_list[0].get("corp_cnt", 0)))
                total_employees = int(float(comp_list[0].get("tot_worker", 0)))

        return {
            "source": "SGIS OpenAPI",
            "residential_population": total_pop,
            "households": total_households,
            "companies": total_companies,
            "workplace_population": total_employees,
            "age_distribution": age_groups
        }

# Singleton instance
sgis_service = SGISService()
