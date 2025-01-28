# proxyrequest/utils.py
import requests
from typing import Optional, Dict

def proxy_verifier(proxy: Optional[Dict[str, str]] = None, url: str = "http://httpbin.org/ip", timeout: int = 5, headers: Optional[Dict[str, str]] = None, verify: bool = True) -> bool:
    """
    Checks whether the given proxy is working by making a simple HTTP request to a test URL.
    If no proxy is provided, it fetches the public IP directly.

    Args:
        proxy (dict, optional): The proxy configuration (e.g., {"http": "http://proxy_ip:port", "https": "https://proxy_ip:port"}). Default is None.
        url (str): The URL to test the proxy against. Default is http://httpbin.org/ip.
        timeout (int): The timeout value for the request in seconds. Default is 5 seconds.
        headers (dict, optional): Custom headers to be sent with the request. Default is None, which sends a standard User-Agent.
        verify (bool, optional): Whether to verify SSL certificates. Default is True. Set to False if you want to skip SSL verification.

    Returns:
        bool: True if the proxy is working, False otherwise.
    """
    # If no proxy is provided, default to an empty dictionary
    if proxy is None:
        proxy = {}

    # If no custom headers are provided, use a default User-Agent header
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    try:
        # If no proxy is given, get the public IP directly
        if not proxy:
            print(url)
            response = requests.get(url, headers=headers, timeout=timeout, verify=verify)
        else:
            # Sending a GET request to the test URL using the proxy, custom headers, timeout, and SSL verification
            response = requests.get(url, proxies=proxy, headers=headers, timeout=timeout, verify=verify)
        
        # If the status code is 200, the proxy is working or we got the IP
        if response.status_code == 200:
            if not proxy:
                # If no proxy, just print and return the public IP
                public_ip = response.json().get("origin", "Unknown")
                print(f"Public IP is used: {public_ip}")
                return True
            else:
                # If proxy was used, print success
                print(f"Proxy {proxy} is working!")
                return True
        else:
            print(f"Failed with status code {response.status_code}")
            return False    

    except requests.exceptions.ConnectTimeout:
        print(f"Error: timeout")
        return False

    except requests.exceptions.ConnectionError:
        print(f"Error: check net connections")
        return False

    except requests.exceptions.SSLError:
        print(f"Error: certificate verify failed (SSL)")
        return False

    except requests.exceptions.JSONDecodeError:
        print(f"Error: decoding JSON")
        return False

    except requests.exceptions.ReadTimeout:
        print(f"Error: ReadTimeout")
        return False        

    except Exception as error:
        print(error)
        return False 

def ip_details(ip_address: str) -> Optional[Dict[str, str]]:
    """
    Fetches IP details from ip-api.com.

    Args:
    - ip: IP address to fetch details for.

    Returns:
    - A dictionary with details like 'IP', 'City', 'Region', 'Country', 'Location', and 'ISP/Org'.
    - Returns None if there's an error or no data is available.
    """
    url = f"http://ip-api.com/json/{ip_address}"
    try:
        response = requests.get(url)
        json_data = response.json()
        status = json_data.get("status","")
        if response.status_code == 200 and status =="success":
            data_dict = dict()
            query = json_data.get("query","")

            # ================Address==================
            continent = json_data.get("continent","")
            continent_code = json_data.get("continentCode","")
            country = json_data.get("country","")
            country_code = json_data.get("countryCode","")
            region = json_data.get("region","")
            region_name = json_data.get("regionName","")
            city = json_data.get("city","")
            district = json_data.get("district","")
            postal = json_data.get("zip","")
            latitude = json_data.get("lat","")
            longitude = json_data.get("lon","")
            address = {"continent":continent,"continent_code":continent_code,"country":country,"country_code":country_code,"region":region,"region_name":region_name,"city":city,"district":district,"postal":postal,"latitude":latitude,"longitude":longitude}

            # ================Service Provider==================
            isp = json_data.get("isp","")
            organization = json_data.get("org","")
            as_numer = json_data.get("as","")
            as_name = json_data.get("asname","")
            mobile = json_data.get("mobile","")
            proxy = json_data.get("proxy","")
            hosting = json_data.get("hosting","")
            service_provider = {"isp":isp,"organization":organization,"as_numer":as_numer,"as_name":as_name,"mobile":mobile,"proxy":proxy,"hosting":hosting}

            timezone = json_data.get("timezone","")
            offset = json_data.get("offset","")
            currency = json_data.get("currency","")

            # =================Return data====================
            data_dict["query"] = query
            data_dict["status"] = status
            data_dict["address"] = address
            data_dict["timezone"] = timezone
            data_dict["offset"] = offset
            data_dict["currency"] = currency
            data_dict["service_provider"] = service_provider
            return data_dict
        else:
            return json_data

    except Exception as error:
        return {"query":ip_address, "status":error}        
   