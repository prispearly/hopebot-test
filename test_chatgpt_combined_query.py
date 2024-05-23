
import logging
import openai
import os
from fetch_frm_gsheets import fetch_gsheets_html, fetch_values_from_html, fetch_content_from_row

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("ai_token")



google_sheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQzZxOdW4jNDNDwRPrE7NlPKF_8vTJI7YlqEUabvW0ogYgoP9rzT0C0DXBFhm01iNhenGCgeXjUJi1k/pubhtml?gid=1564820060&single=true'

html = fetch_gsheets_html(google_sheet_url)



def gpt(input1, input2, chatgpt_role):
  """
  Function to interact with OpenAI's GPT-3 model.
  """
  # Construct messages list based on inputs and specified roles
  messages = [
    {
      "role": "system",
      "content": chatgpt_role
    },
    {
      "role": "system",
      "content": input1 + input2
    },
  ]

  # Call OpenAI's ChatCompletion API
  response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                          messages=messages,
                                          temperature=0.5,
                                          max_tokens=500,
                                          top_p=1,
                                          frequency_penalty=0.0,
                                          presence_penalty=0.0)

  # Get generated text from response
  generated_text = response.choices[0].message.content

  # Append generated text to messages list
  messages.append({"role": "assistant", "content": generated_text})

  return generated_text


input1 = "when is the next art of marriage retreat, is there another one after may?"

input2 = str(fetch_values_from_html(1, html))
# input2 = '''
# ['Art of Marriage Retreat 17-18 Aug 2024 (Sat-Sun)', 'Art Of Marriage 3D2N Retreat (24-26 May 2024)', 'Marriage Preparation Course (Aug 2024)', 'Keeping Your Covenant Small Group for Married Couples (July 2024)', 'HomeBuilders Small Group for Married Couples', "Pay It Forward (For Aug'23 AOM Participants)"]
# '''

chatgpt_role = "enumerate the items in input 2, return as output, in the form of a list of integers, which items in input 2 best matches the query in input 1, you may return a list with more than one item"

selected_row = gpt(input1, input2, chatgpt_role)
import re
# Use regular expression to find digits in the string
numbers = re.findall(r'\d+', selected_row)

# Convert the first number found to an integer
if numbers:
    selected_row_int = int(numbers[0]) # so dangerous WTH
    print(selected_row_int)  # Output: 2
else:
    print("No number found in the selected_row string.")




input1 = "when is the next art of marriage retreat, is there another one after may?"
input2 = fetch_content_from_row(selected_row_int, html)

# input2 = '''
# Content from column 3 , row 1 : Art Of Marriage 3D2N Retreat (24-26 May 2024)6 video sessions (English audio and subtitles)based on biblical principles:Session 1Love Happens (Purpose of Marriage)Session 2Love Fades (Drift to Isolation)Session 3Love Dances (Roles)Session 4Love Interrupted (Communication)Session 5Love Sizzles (Romance & Sex)Session 6Love Always (Legacy)Highlights* Expert interviews* Real-life stories* Humorous vignettes* Couple projects* Time with spouse (minimal interaction with other couples)Things to note* Transport to and from the hotel on your own (15-min drive from JB CIQ)* Check-in at hotel reception on your own with your passports, anytime from Day 1, 3pm* Retreat program starts on Day 2 (Refer to Schedule)* Parking for hotel guests at RM5 nett per entry (every 24 hours or part thereof), validation at Hotel Reception is required* Passports must be valid for at least 6 months at time of retreat* FamilyLife Singapore will not be liable for any loss incurred due to our event* Participants are encouraged to purchase own travel insuranceWhat the ticket price includes*1 ticket for 1 couple* 2 nights' stay (Double Urban room)* Conference with full-color manuals* Breakfast, lunch & tea-breaks on Days 2 & 3* Malaysia tourism tax* Excludes room service, parking fee, and other incidentalsTo Register* Click on an option box* Closing date: 5 May* Registration full or closed? Emailuson vacancies.ScheduleFAQsTestimonies sign up at: http://Cru.sg/aom3D2N
# '''

chatgpt_role = "help me answer the user's question in input1, based on the info in input2, and provide other general info about the event as well in addition to the question, include date, Dates & Time: Venue: Cost: Closing Date: Link to register:. For more information, FAQs, and testimonies, you can visit the registration link provided above."

print(gpt(input1, input2, chatgpt_role))

