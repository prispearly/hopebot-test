import json
import openai

def get_message_from_json(file_path):
    # Read and return the JSON content from the specified file path
    with open(file_path, 'r') as file:
        message = json.load(file)
    return message

def gpt(message):
    """
    Function to interact with OpenAI's GPT-3 model.
    """
    messages = [{
        "role":
        "system",
        "content":
        "You are a friend who is here to walk alongside you on your journey of understanding faith and Christianity. Just like a friend, you are here to offer personable explanations, making complex concepts simple and relatable. Whether the user is curious about the meaning of Easter, wondering what God is like, or exploring how faith impacts everyday life, you are here to help. Summarize answers in a friendly manner using layman's terms, as if explaining to a friend. We want our bot to reflect a Christian biblical worldview, emphasizing the love of God and the practical impact of faith. Focus on guiding users to understand Easter's meaning, what God is like, and how Christianity influences daily life. Instead of explaining things as divine justice or Christian faith and practice, let us talk from the perspective of a relationship with our loving Father in heaven. Christianity is not just stories; it is rooted in historical truth. Try to limit the text to a maximum of 300 tokens. Respond where appropriate - in point form and with certain titles. Keeps answers summarised and succinct. Space sentences out with paragraph breaks where appropriate to help readability."
    }]
    messages.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                            messages=messages,
                                            temperature=0.5,
                                            max_tokens=500,
                                            top_p=1,
                                            frequency_penalty=0.0,
                                            presence_penalty=0.0)
    generated_text = response.choices[0].message.content
    messages.append({"role": "assistant", "content": generated_text})
    return generated_text


def modified_gpt(input1, input2, chatgpt_role):
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

def gpt_remove_emails(content):
    
    chatgpt_role = """
    you will be given event detail content
    help me remove all emails as contact info for this event
    the resultant text should not contain any email info
    
    and please leave out email as a form of contact
    
    and please do not suggest things like:
    For any further questions or assistance, you can reach out to the event organizers, and they will reply within 3 working days.
    
    we would not like to direct users to contact the event organisers, all questions should be answered by you the chatbot
    in your response to them
    """
    message = '' #empty message
    answer = modified_gpt(message, content, chatgpt_role)
    return answer