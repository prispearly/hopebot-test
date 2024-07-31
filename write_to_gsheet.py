import gspread
from google.oauth2.service_account import Credentials


def write_data_to_sheet(data, spreadsheet_name, worksheet_title):

          # Path to your service account JSON file
          SERVICE_ACCOUNT_FILE = './config/gspread/service_account.json'

          # Define the scope
          SCOPES = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
          ]

          # Load the credentials from the service account file
          creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE,
                                                        scopes=SCOPES)

          # Authenticate with Google Sheets API
          gc = gspread.authorize(creds)

          # Open the Google Sheet by its name
          spreadsheet = gc.open(spreadsheet_name)

          # Get the worksheet by title
          worksheet = spreadsheet.worksheet(worksheet_title)

          # clear previous periodic data
          worksheet.clear()
          
          # Write data to the Google Sheet
          worksheet.append_rows(data)
          print("Data successfully written to Google Sheet!")


# # Example usage:
# data_to_write = [
#     ["John", "Doe", 30],
#     ["Jane", "Smith", 25],
#     ["Alice", "Johnson", 35]
# ]

# write_data_to_sheet(data_to_write, "test_gsheet", "event info")
