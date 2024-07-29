import requests
from bs4 import BeautifulSoup


def fetch_gsheets_html(url):
    """Fetches HTML content from the provided URL."""
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.text


def extract_column_values(html, column_index):
    """
    Extracts values from the specified column index of the HTML table.
    Assumes the table structure is consistent across the HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")

    column_values = []

    for table in tables:
        for row in table.find_all("tr"):
            cells = row.find_all("td")

            # Check if the row is not empty and contains the specified column index
            if len(cells) > column_index:
                # Extract data from the specified column index
                column_value = cells[column_index].text.strip()

                # Append the value to the list
                if column_value:
                    column_values.append(column_value)

    return column_values

def fetch_values_from_html(column_index, html):
    # Example 1: Fetch values from column 2
    # column_index = 1  # Indexing starts from 0
    column_values = extract_column_values(html, column_index)
    print("Values from column", column_index + 1, ":", column_values)
    return column_values


def fetch_content_from_row(row_index, html):

    # row index starts from 0 
    print("GSHEETS ROW FETCHING FROM:", row_index)
    
    # Example 2: Fetch content from column 3 of a specific row
    # row_index = 1  # Change this to the desired row index

 
    column_index = 2  # Indexing starts from 0
    content = extract_column_values(html, column_index)[row_index]
    
    sign_up_link = extract_column_values(html, 0)[row_index]
    
    content = content + " sign up at: " + sign_up_link
    print("ITS ALL GONE WRONG HERE OR NOT:")
    
    if content is not None:
        print("Content from column", column_index + 1, ", row", row_index, ":",
              content)
    else:
        print("Row", row_index, "not found or does not contain data in column",
              column_index + 1)
    return content
    
def main():
    google_sheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQzZxOdW4jNDNDwRPrE7NlPKF_8vTJI7YlqEUabvW0ogYgoP9rzT0C0DXBFhm01iNhenGCgeXjUJi1k/pubhtml?gid=1564820060&single=true'

    html = fetch_gsheets_html(google_sheet_url)
    column_values = fetch_values_from_html(1, html)
    content = fetch_content_from_row(1, html)
    # print(column_values)
    # print(content)


if __name__ == "__main__":
    main()
