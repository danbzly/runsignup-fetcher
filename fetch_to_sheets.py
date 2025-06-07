import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests

# Set up Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open your sheet
sheet = client.open("Race Results").sheet1

# RunSignUp API
RACE_ID = "127835"
RESULT_SET_ID = "535508"
url = f"https://runsignup.com/rest/race/{RACE_ID}/results/{RESULT_SET_ID}"

def fetch_results():
    response = requests.get(url)
    data = response.json()
    return data.get("results", [])

def update_sheet(results):
    sheet.clear()
    # Re-add headers
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
            result.get("city", ""),
            result.get("state", "")
        ]
        sheet.append_row(row)

if __name__ == "__main__":
    race_results = fetch_results()
    update_sheet(race_results)
    print("✅ Results updated to Google Sheet!")

