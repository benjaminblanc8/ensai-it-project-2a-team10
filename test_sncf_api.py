import json
import os

import requests
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

API_KEY = os.getenv("SNCF_API_KEY")

if not API_KEY:
    raise RuntimeError("SNCF_API_KEY is missing. Add it to your .env file.")

BASE_URL = "https://api.sncf.com/v1/coverage/sncf/"


def test_get_stops():
    """Test the SNCF stop areas endpoint."""
    url = f"{BASE_URL}stop_points/"

    response = requests.get(url, auth=(API_KEY, ""))

    response.raise_for_status()

    print("GET:", url)
    print("Status:", response.status_code)

    response.raise_for_status()

    data = response.json()

    print("Response keys:", list(data.keys()))
    print("Number of stop areas:", len(data.get("stop_areas", [])))

    return data


def test_get_journey(from_station, to_station, datetime):
    """Test the SNCF journeys endpoint."""
    url = f"{BASE_URL}journeys"

    params = {
        "from": from_station,
        "to": to_station,
        "datetime": datetime,
    }

    headers = {"Authorization": f"Bearer {API_KEY}"}

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=30,
    )

    print("GET:", response.url)
    print("Status:", response.status_code)

    response.raise_for_status()

    data = response.json()

    print("Response keys:", list(data.keys()))
    print("Number of journeys:", len(data.get("journeys", [])))

    return data


def test_get_stops_by_name(name):
    url = f"{BASE_URL}places"

    params = {"q": name, "type[]": "stop_area"}

    response = requests.get(url, params=params, auth=(API_KEY, ""))

    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    print("=== Testing SNCF API ===")

    # Test 1: stop areas
    print("\n--- GET stop areas ---")
    try:
        stops = test_get_stops()
        stops_by_name = test_get_stops_by_name("Aban")

        # Export JSON
        with open("stations.json", "w", encoding="utf-8") as file:
            json.dump(stops_by_name, file, ensure_ascii=False, indent=4)

        print("Request succeeded.")
        print("JSON exported to stations.json")

    except requests.exceptions.HTTPError as e:
        print("HTTP error:", e)
        print("Response:", e.response.text[:1000])

    except requests.exceptions.RequestException as e:
        print("Request error:", e)
    # Test 2: journeys
    #
    # Uncomment and replace the station IDs with valid SNCF stop_area IDs.
    #
    # print("\n--- GET journeys ---")
    # try:
    #     journey = test_get_journey(
    #         from_station="stop_area:ID_OF_DEPARTURE",
    #         to_station="stop_area:ID_OF_ARRIVAL",
    #         datetime="20260925T120000",
    #     )
    #     print("Request succeeded.")
    # except requests.exceptions.HTTPError as e:
    #     print("HTTP error:", e)
    #     print("Response:", e.response.text[:1000])
    # except requests.exceptions.RequestException as e:
    #     print("Request error:", e)
