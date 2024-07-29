from googleapiclient.discovery import build
from google.oauth2 import service_account
import requests
from bs4 import BeautifulSoup
import urllib
from write_to_gsheet import write_data_to_sheet
from datetime import datetime
from clean_titles import clean_and_return_title

# Google Sheets API setup
SERVICE_ACCOUNT_FILE = 'config/gspread/service_account.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# https://www.googleapis.com/auth/spreadsheets.readonly,

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID and range of the spreadsheet.
# SHEET_NAME = 'test_gsheet'
SPREADSHEET_ID = '1AKYsr-zAoYIObsOwuaS4JE9eJL_z47e3sMYUpbh0g8k'
RANGE_NAME = 'Form Responses 1'


def fetch_google_sheet():
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found in the Google Sheet.')
        return None, None, None

    # Extract the latest row data
    latest_row = values[-1]
    timestamp, event_link, email_address = latest_row[0], latest_row[1], latest_row[2]

    return timestamp, event_link, email_address

def separate_links(concatenated_links_str):
    separated_links = concatenated_links_str.split("http://")
    separated_links = [link for link in separated_links if link]
    separated_links_list = ['http://' + link for link in separated_links]
    return separated_links_list

def get_redirected_url(url):
    try:
        with urllib.request.urlopen(url) as response:
            redirected_url = response.geturl()
            return redirected_url
    except urllib.error.URLError as e:
        print("Error:", e)
        return None

def scrape_event_text_from_link(url):
    text_content = ""
    redirected_url = get_redirected_url(url)
    if not redirected_url:
        return text_content

    response = requests.get(redirected_url)
    if response.status_code != 200:
        print(f"Failed to fetch {redirected_url}: {response.status_code}")
        return text_content

    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('div', class_='hero-cap event-name')
    if title:
        cleaned_titles = clean_and_return_title(title)
        text_content += cleaned_titles

    buttons = soup.find_all('button', class_="rounded-0 w-100 btn_1 btn boxed-btn mb-3")
    for button in buttons:
        text_content += button.get_text(strip=True)

    span_tags = soup.find_all(
        'span', style=lambda style: style and 'font-size:11pt' in style)
    for span in span_tags:
        text_content += span.get_text(strip=True)

    return text_content, str(cleaned_titles)

def main():
    timestamp, event_link, email_address = fetch_google_sheet()

    if not timestamp or not event_link:
        print("No data found in the Google Sheet.")
        return

    separated_links_list = separate_links(event_link)
    print("LINKS FROM GSHEETS FETCHED", separated_links_list)

    data = []
    for link in separated_links_list:
        event_text, title = scrape_event_text_from_link(link)
        data.append([link, title, event_text, str(datetime.now())])

    write_data_to_sheet(data, SPREADSHEET_ID, "latest event info")

if __name__ == "__main__":
    main()