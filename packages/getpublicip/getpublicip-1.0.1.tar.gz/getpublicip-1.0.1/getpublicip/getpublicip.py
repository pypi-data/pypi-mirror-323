import requests
from requests.exceptions import RequestException
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def welcome():
    """Fetch and print the public IP address using requests."""
    try:
        print("Fetching public IP address...")
        response = requests.get("https://api.ipify.org?format=text", verify=False, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses
        print(f"Your public IP address is: {response.text}")
    except RequestException as e:
        print(f"Error occurred during the HTTP request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
