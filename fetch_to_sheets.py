import os
import json
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import csv
import pandas as pd

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

# Fetch CSV from URL
RACE_ID = "21"  # Hardcoded for now, can be made dynamic later
CSV_URL = f"https://kzmid2emy2xxhkskn3go.lite.vusercontent.net/api/race-data?race_id={RACE_ID}&format=csv"

def fetch_results():
    try:
        # Download CSV
        response = requests.get(CSV_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        print("CSV URL:", CSV_URL)
        print("CSV response status code:", response.status_code)
        print("CSV response text (first 500 chars):", response.text[:500])

        # Load CSV into pandas DataFrame
        df = pd.read_csv(CSV_URL)
        print(f"Loaded {len(df)} rows from CSV")

        # Convert DataFrame to list of dictionaries for gspread
        results = df.to_dict(orient="records")
        print("First result:", results[0] if results else "No results")
        return results
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CSV data: {e}")
        raise
    except Exception as e:
        print(f"Error processing CSV data: {e}")
        raise

def update_sheet(results):
    try:
        sheet.clear()
        print("Cleared Google Sheet")

        # Get headers from the first row of the DataFrame
        headers = list(results[0].keys()) if results else []
        sheet.append_row(headers)  # Write dynamic headers from CSV
        print(f"Appended header row: {headers}")

        # Write data rows
        for i, result in enumerate(results, 1):
            row = [result.get(header, "") for header in headers]
            sheet.append_row(row)
            print(f"Appended row {i}: {row}")
        print("Successfully updated Google Sheet")
    except Exception as e:
        print(f"Error updating Google Sheet: {e}")
