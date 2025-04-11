from googleapiclient.discovery import build
from google.oauth2 import service_account
import requests
import re
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

def is_valid_url(link):
    # Regex pattern to check if the link is a valid URL format
    pattern = re.compile(r'^(http:\/\/|https:\/\/)?[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}.*$')
    return bool(pattern.match(link)) 

def separate_links(concatenated_links_str):
    separated_links = concatenated_links_str.split("http://")
    separated_links = [link.strip() for link in separated_links if link.strip()]  # Strip whitespace
    separated_links_list = ['http://' + link for link in separated_links if is_valid_url('http://' + link)]
    return separated_links_list


def is_valid_event_url(link):
    return link.startswith("https://mde.cru.org.sg/")

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
    cleaned_title = "" 

    redirected_url = get_redirected_url(url)
    
    if not is_valid_event_url(redirected_url):
        error_msg = f" not valid event URL: {redirected_url}, original short URL: {url}. Check if short URL leads to correct MDE link. "
        print(error_msg)
        return error_msg, cleaned_title    
    if not redirected_url:
        error_msg = f" unable to get redirected URL: {redirected_url}, short URL: {url}. Check if short URL is correct. "
        print(error_msg)
        return error_msg, cleaned_title

    response = requests.get(redirected_url)
    if response.status_code != 200:
        error_msg = f"Failed to fetch {redirected_url}: {response.status_code}"
        print(error_msg)
        return error_msg, cleaned_title

    ## webscraping based on specific html fonts
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('div', class_='hero-cap event-name')
    
    # Handle case if title is None
    if title:
        cleaned_title = clean_and_return_title(title)
        text_content += cleaned_title
    else:
        error_msg = f"No event found for URL: {redirected_url}, original URL: {url}. Check if URL is correct. "
        print(error_msg)
        return error_msg, cleaned_title
        
        
    buttons = soup.find_all('button', class_="rounded-0 w-100 btn_1 btn boxed-btn mb-3")
    for button in buttons:
        text_content += button.get_text(strip=True)
    
    # scrape several types of content text
    # Find the specific div containing the text
    content_div = soup.find('div', class_='ck-content')
    # Loop through all paragraphs and span tags within the div
    if content_div:
        for tag in content_div.find_all(['p', 'span']):
            text_content += tag.get_text(strip=True) + ' '
    span_tags = soup.find_all(
        'span', style=lambda style: style and 'font-size:11pt' in style)
    if span_tags:
        for span in span_tags:
            text_content += span.get_text(strip=True)

    return text_content, str(cleaned_title)

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