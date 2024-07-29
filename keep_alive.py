import gspread
from bs4 import BeautifulSoup
import requests
import logging

import os
import monthly_webscrape_and_write_to_gsheets

from google.oauth2.service_account import Credentials
from flask import Flask, request, jsonify
from threading import Thread
from dotenv import load_dotenv
from fetch_frm_gsheets import fetch_gsheets_html, fetch_values_from_html, fetch_content_from_row

from helper_functions import *

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("ai_token")

# Initialize Flask app
app = Flask(__name__)
    


@app.route('/', methods=['GET'])
def index():
    """
    Endpoint to check if the server is running.
    """
    return "Alive"


@app.route('/gformsubmit', methods=['POST'])
def gformsubmit():
    """
    Endpoint that triggers webscraping from links once google form submitted.
    """
    monthly_webscrape_and_write_to_gsheets.main()
    return "Done"


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint to handle Kommunicate webhook requests.
    """
    webhook_data = request.json
    # Extract necessary information from the request
    bot_id = webhook_data.get('botId')
    key = webhook_data.get('key')
    user_id = webhook_data.get('from')
    message_frm_kommunicate = webhook_data.get('message')
    matched_intent = webhook_data.get('matchedIntent')
    group_id = webhook_data.get('groupId')
    metadata = webhook_data.get('metadata')
    content_type = webhook_data.get('contentType')
    app_id = webhook_data.get('applicationKey')
    source = webhook_data.get('source')
    event_name = webhook_data.get('eventName')
    created_at = webhook_data.get('createdAt')
    logger.info(
        "Webhook received: bot_id=%s, key=%s, user_id=%s, message=%s, matched_intent=%s, group_id=%s, metadata=%s, content_type=%s, app_id=%s, source=%s, event_name=%s, created_at=%s",
        bot_id, key, user_id, message_frm_kommunicate, matched_intent,
        group_id, metadata, content_type, app_id, source, event_name,
        created_at)
    gpt_message = gpt(message_frm_kommunicate)
    response = [{"message": gpt_message}]
    return jsonify(response)


@app.route('/event', methods=['POST'])
def event_query():
    """
    Endpoint to handle event queries.
    """
    request_body = request.json

    message = request_body['message']

    print("Query from user: ", message)

    # Load OpenAI API key from environment variable
    openai.api_key = os.getenv("ai_token")

    # warning: this gsheets is only updated every 5 min
    google_sheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQzZxOdW4jNDNDwRPrE7NlPKF_8vTJI7YlqEUabvW0ogYgoP9rzT0C0DXBFhm01iNhenGCgeXjUJi1k/pubhtml?gid=1564820060&single=true'

    html = fetch_gsheets_html(google_sheet_url)

    # input1 = "when is the next art of marriage retreat, is there another one after may?"
    input2_list = fetch_values_from_html(1, html)
    input2 = str(input2_list)
    # input2 = '''
    # ['Art of Marriage Retreat 17-18 Aug 2024 (Sat-Sun)', 'Art Of Marriage 3D2N Retreat (24-26 May 2024)', 'Marriage Preparation Course (Aug 2024)', 'Keeping Your Covenant Small Group for Married Couples (July 2024)', 'HomeBuilders Small Group for Married Couples', "Pay It Forward (For Aug'23 AOM Participants)"]
    # '''
    
    

    chatgpt_role_1 = """
    you will be given a user question and a list of possible matching events, enumerate the events in the list, starting from 0. Return as output, in the form of a list of integers, which coressponding events in the given list of events best matches the query. you may return a list with more than one integer.
    please only return as output, in the form of a list of integers, dont need to explain the reasoning.
    
    for example 
    query: how can i sign up for AOM
    you may match it with the events:
    Art of Marriage Retreat 17-18 Aug 2024 (Sat-Sun)
    Art Of Marriage 3D2N Retreat (24-26 May 2024)
    and thereby return integers:
    [0, 1]

    query: how can i join a homebuilders small group
    you may match it with the event:
    HomeBuilders Small Group for Married Couples
    (for example, returning the number which corresponds, since the query about (homebuilder) matches with the event about (homebuilders))
    and thereby return integer: [4] 
 
    query: how can i join a keeping your covenant
    you may match it with the event:
    Keeping Your Covenant Small Group for Married Couples (July 2024)
    (for example, returning the number which corresponds, since the query about (Keeping Your Covenant) matches with the event about (keeping your covenant))
    and thereby return integer: [8] 
    
    
    """

    # temp put here - input2
    # input2_list = ['Art of Marriage Retreat 17-18 Aug 2024 (Sat-Sun)', 'Art Of Marriage 3D2N Retreat (24-26 May 2024)', 'Marriage Preparation Course (Aug 2024)', 'Art of Parenting Small Group (Feb 2024)', 'Art of Parenting Free Preview (12 Oct 2024)', "Stepping Up Men's Series & Free Preview (Sep - Nov 2024)", 'Keeping Your Covenant Small Group for Married Couples (July 2024)', 'HomeBuilders Small Group for Married Couples', "Pay It Forward (For Aug'23 AOM Participants)"]
    # input2 = str(input2_list)
    selected_row = modified_gpt(message, input2, chatgpt_role_1)
    print("MATCHED CATEGORY:", selected_row)


    import re
    # Use regular expression to find digits in the string
    numbers = re.findall(r'\d+', selected_row)
        # Initialize selected_row_int as None
    selected_row_int = None

    # Check if numbers list is not empty and input2_list is valid
    if numbers and len(input2_list) > 0:
        for num in numbers:
            try:
                # Convert the current number to an integer
                candidate_int = int(num)
                
                # Check if the converted integer is within the valid index range
                if 0 <= candidate_int < len(input2_list):
                    selected_row_int = candidate_int
                    break  # Exit for loop once a valid number is found
                print("integer out of list length")            
            except ValueError:
                # Handle cases where conversion fails
                print(f"'{num}' is not a valid integer.")

    # Check if a valid integer was found
    if selected_row_int is not None:
        print(f"Selected event: {input2_list[selected_row_int]}")
    else:
        print("No valid number found in the specified range.")


    # # Convert the first number found to an integer
    # if numbers:
    #     selected_row_int = int(numbers[0])  # so dangerous WTH

    #     print("MATCHED INTEGER:", selected_row_int) 
    #     # print("MATCHED CATEGORY:", selected_row_int, input2_list[selected_row_int])

    # else:
    #     print("No number found in the selected_row string.")
        
            
    # done1: check if text from selected_row in gsheet says "stay tuned" -> reply set answer  
    """
    if column_values contains "stay tuned"
    """
    # return column values
    gsheet_content = fetch_content_from_row(selected_row_int, html)
    if "stay tuned" in gsheet_content:
        message_file_path = "config/rich-messaging-templates/subscribe_for_next_runs.json"
        json_message = get_message_from_json(message_file_path)
        message = [json_message,]
        return jsonify(message) 


    # input1 = "when is the next art of marriage retreat, is there another one after may?"
    input2 = gsheet_content

    # input2 = '''
    # Content from column 3 , row 1 : Art Of Marriage 3D2N Retreat (24-26 May 2024)6 video sessions (English audio and subtitles)based on biblical principles:Session 1Love Happens (Purpose of Marriage)Session 2Love Fades (Drift to Isolation)Session 3Love Dances (Roles)Session 4Love Interrupted (Communication)Session 5Love Sizzles (Romance & Sex)Session 6Love Always (Legacy)Highlights* Expert interviews* Real-life stories* Humorous vignettes* Couple projects* Time with spouse (minimal interaction with other couples)Things to note* Transport to and from the hotel on your own (15-min drive from JB CIQ)* Check-in at hotel reception on your own with your passports, anytime from Day 1, 3pm* Retreat program starts on Day 2 (Refer to Schedule)* Parking for hotel guests at RM5 nett per entry (every 24 hours or part thereof), validation at Hotel Reception is required* Passports must be valid for at least 6 months at time of retreat* FamilyLife Singapore will not be liable for any loss incurred due to our event* Participants are encouraged to purchase own travel insuranceWhat the ticket price includes*1 ticket for 1 couple* 2 nights' stay (Double Urban room)* Conference with full-color manuals* Breakfast, lunch & tea-breaks on Days 2 & 3* Malaysia tourism tax* Excludes room service, parking fee, and other incidentalsTo Register* Click on an option box* Closing date: 5 May* Registration full or closed? Emailuson vacancies.ScheduleFAQsTestimonies sign up at: http://Cru.sg/aom3D2N
    # '''

    chatgpt_role_2 = """
    help me answer the user's question in input1, based on the info in input2, and provide other general info about the event as well in addition to the question, include date, Dates & Time: Venue: Cost: Closing Date: Link to register:. For more information, you can visit the registration link provided above.
    """

    answer = modified_gpt(message, input2, chatgpt_role_2)
    print(answer)

    message = [{
        "message": answer 
    }, ]

    return jsonify(message)


@app.route('/test', methods=['POST'])
def test():
    """
    Endpoint for testing purposes.
    """
    html = requests.get(
        'https://docs.google.com/spreadsheets/d/e/2PACX-1vSU95oUetvlBecIjdCElWiHVdtT1BxuuMj3xzi7Mv3n9NHFJIy_cI63vwi3J4DBX8KU89ynR91qy_Cv/pubhtml'
    ).text
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")
    for table in tables:
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            for i, cell in enumerate(cells):
                if cell.text.strip() == "Art of Marriage":
                    if i < len(cells) - 1:
                        output = cells[i + 2].text.strip()
    return jsonify([{"message": output}])


def run():
    """
    Function to run the Flask app.
    """
    app.run(host='0.0.0.0', port=80)


def keep_alive():
    """
    Function to start the Flask app in a separate thread.
    """
    t = Thread(target=run)
    t.start()


if __name__ == '__main__':
    keep_alive()
