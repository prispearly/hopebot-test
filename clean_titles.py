import re
from bs4 import BeautifulSoup

def clean_and_return_title(s):
    # Define a regex pattern to match control characters
    control_char_pattern = re.compile(r'[\x00-\x1F\x7F-\x9F]')

    # Replace control characters with an empty string
    clean_s = control_char_pattern.sub('', str(s))
    # clean_s = clean_s.replace(" ", "%20")


    # Parse the HTML string using BeautifulSoup
    soup = BeautifulSoup(clean_s, 'html.parser')

    # Find the specific element you need
    title_tag = soup.find('div', class_='hero-cap event-name')

    # Extract the text from the <h2> tag
    title_text = title_tag.find('h2').get_text(strip=True)
    # print("Title Text:", title_text)

    return title_text

# Example usage
# url_with_control_chars = '<div class="hero-cap event-name"><h2 data-animation="fadeInLeft" data-delay=".6s">Pay It Forward (For Aug\'23 AOM Participants)<'

url_with_control_chars = '<div class="hero-cap event-name"><h2 data-animation="fadeInLeft" data-delay=".6s">Art of MarriageRetreat 17-18 Aug 2024 (Sat-Sun)</h2></div>'

title_text = clean_and_return_title(url_with_control_chars)
# print("Cleaned URL:", clean_url)
