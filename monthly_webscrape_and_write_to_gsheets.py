from bs4 import BeautifulSoup
import requests
import urllib
from write_to_gsheet import write_data_to_sheet
from datetime import datetime
from clean_titles import clean_and_return_title


# Function to fetch and parse the Google Sheet HTML
def fetch_google_sheet(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.text


# Function to extract data from the Google Sheet
def extract_sheet_data(html):
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")

    timestamps = []
    event_links = []
    email_addresses = []

    for table in tables:
        # Find all rows and iterate in reverse order
        rows = table.find_all("tr")
        # print("CHECK ROW DATA HERE", rows)

        for row in reversed(rows):
            cells = row.find_all("td")
            row_data = [cell.text.strip() for cell in cells]

            # print("CHECK ROW DATA HERE", row_data)

            # Check if the row is not empty and contains at least 3 cells
            if row_data and len(row_data) >= 3:
                # Extract data from the row
                timestamp, event_link, email_address = row_data[0], row_data[
                    1], row_data[2]
                return timestamp, event_link, email_address

    # Return None if no valid rows are found
    return None, None, None

    # Append data to respective lists
    timestamps.append(timestamp)
    event_links.append(event_link)
    email_addresses.append(email_address)

    return timestamps, event_links, email_addresses


# Function to separate concatenated links
def separate_links(concatenated_links_str):
    # Split the string based on the delimiter 'http://'
    separated_links = concatenated_links_str.split("http://")

    # Remove the empty string resulting from the split
    separated_links = [link for link in separated_links if link]

    # Add 'http://' back to each link except the first one
    separated_links_list = ['http://' + link for link in separated_links]

    return separated_links_list


# Function to get the redirected URL
def get_redirected_url(url):
    try:
        with urllib.request.urlopen(url) as response:
            redirected_url = response.geturl()
            return redirected_url
    except urllib.error.URLError as e:
        print("Error:", e)
        return None


# Function to scrape event text from a link
def scrape_event_text_from_link(url):
    text_content = ""
    # print("HERRRRRREEE", url)
    redirected_url = get_redirected_url(url)
    if not redirected_url:
        return text_content

    # Send a GET request to the redirected URL
    response = requests.get(redirected_url)
    if response.status_code != 200:
        print(f"Failed to fetch {redirected_url}: {response.status_code}")
        return text_content

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the main content
    title = soup.find('div', class_='hero-cap event-name')
    if title:
        cleaned_titles = clean_and_return_title(title)
        text_content += cleaned_titles
        # print("TITLE HERE",cleaned_titles)

    # Extract button elements
    buttons = soup.find_all('button',
                            class_="rounded-0 w-100 btn_1 btn boxed-btn mb-3")
    for button in buttons:
        text_content += button.get_text(strip=True)

    # Extract span tags with specific style
    span_tags = soup.find_all(
        'span', style=lambda style: style and 'font-size:11pt' in style)
    for span in span_tags:
        text_content += span.get_text(strip=True)

    return text_content, str(cleaned_titles)


# Main script
def main():

    ###### step 1: take from this sheet ######
    google_sheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQzZxOdW4jNDNDwRPrE7NlPKF_8vTJI7YlqEUabvW0ogYgoP9rzT0C0DXBFhm01iNhenGCgeXjUJi1k/pubhtml?gid=1577191655&single=true'
    html = fetch_google_sheet(google_sheet_url)

    timestamps, event_links, email_addresses = extract_sheet_data(html)

    print("have the LATEST", extract_sheet_data(html))

    if not timestamps or not event_links:
        print("No data found in the Google Sheet.")
        return

    # Separate concatenated links
    separated_links_list = separate_links(event_links)
    print("LINKS FROM GSHEETS FETCHED", separated_links_list)

    ###### step 2: do webscraping ######
    data = []
    # Scrape event text from each link
    for link in separated_links_list:
        event_text, title = scrape_event_text_from_link(link)
        # print("Event Text:", event_text)
        data.append([link, title, event_text, str(datetime.now())])

    ###### step 3: write to this sheet ######
    write_data_to_sheet(data, "test_gsheet", "latest event info")


if __name__ == "__main__":
    main()
