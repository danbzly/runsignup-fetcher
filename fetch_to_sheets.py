import os, json, base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import xml.etree.ElementTree as ET

# Debug: Check Google credentials
print("GOOGLE_CREDS_JSON exists:", "GOOGLE_CREDS_JSON" in os.environ)
print("GOOGLE_CREDS_JSON length:", len(os.environ.get("GOOGLE_CREDS_JSON", "")))
print("GOOGLE_CREDS_JSON first 50 chars:", os.environ.get("GOOGLE_CREDS_JSON", "")[:50])

# Decode the base64-encoded JSON credentials
try:
    google_creds_base64 = os.environ["GOOGLE_CREDS_JSON"]
    try:
        google_creds_json = base64.b64decode(google_creds_base64).decode("utf-8")
        print("Base64 decoded successfully, length:", len(google_creds_json))
        print("Decoded JSON first 50 chars:", google_creds_json[:50])
    except base64.binascii.Error as e:
        print(f"Base64 decoding failed: {e}")
        raise
    try:
        creds_dict = json.loads(google_creds_json)
        print("JSON parsed successfully")
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        print(f"Full decoded string (first 100 chars): {google_creds_json[:100]}")
        raise
except Exception as e:
    print(f"Error processing credentials: {e}")
    raise

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    print("Google client authorized successfully")
except Exception as e:
    print(f"Error authorizing Google client: {e}")
    raise

# Open your sheet
try:
    sheet = client.open("Race Results").sheet1
    print("Successfully accessed Google Sheet")
except Exception as e:
    print(f"Error accessing Google Sheet: {e}")
    raise

# RunSignUp API
RACE_ID = "6897"
RESULT_SET_ID = "19904"
EVENT_ID = "6897"  # Replace with the correct event_id
url = f"https://runsignup.com/rest/race/{RACE_ID}/results/{RESULT_SET_ID}"

def fetch_results():
    try:
        api_key = os.environ.get("RUNSIGNUP_API_KEY")
        params = {"event_id": EVENT_ID, "format": "json"}  # Request JSON format
        if api_key:
            params["api_key"] = api_key
        response = requests.get(url, params=params)
        print("API URL:", response.url)
        print("API status code:", response.status_code)
        print("API response headers:", response.headers)
        print("API response text (first 500 chars):", response.text[:500])
        response.raise_for_status()

        # Check if response is XML
        if response.headers.get("Content-Type", "").startswith("text/xml"):
            print("API returned XML response")
            try:
                root = ET.fromstring(response.text)
                error = root.find("error")
                if error is not None:
                    error_code = error.find("error_code").text
                    error_msg = error.find("error_msg").text
                    print(f"API error: Code {error_code}, Message: {error_msg}")
                    raise Exception(f"RunSignUp API error: {error_msg} (Code {error_code})")
                else:
                    raise Exception("Unexpected XML response from API")
            except ET.ParseError as e:
                print(f"Error parsing XML response: {e}")
                raise

        # Parse JSON response
        data = response.json()
        print("Successfully fetched API data")
        return data.get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching API data: {e}")
        raise

def update_sheet(results):
    try:
        sheet.clear()
        sheet.append_row(["First Name", "Last Name", "Bib", "Wave", "Time", "Gender", "Age", "Place", "City", "State"])
        for result in results:
            row = [
                result.get("first_name", ""),
                result.get("last_name", ""),
                result.get("bib", ""),
                result.get("wave", ""),
                result.get("chiptime", ""),
                result.get("gender", ""),
                result.get("age", ""),
                result.get("overall_place", ""),
                result.get("city
