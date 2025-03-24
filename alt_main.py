from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the new OpenAI client with your API key
client = OpenAI(api_key=os.getenv("ai_token"))

app = Flask(__name__)

# Global dictionary to maintain conversation history per user
user_histories = {}

def summarize_text(text: str) -> str:
    """
    A simple placeholder function for summarizing text.
    In production, you might call OpenAI's API or another service to generate a proper summary.
    """
    max_chars = 500
    if len(text) > max_chars:
        return text[:max_chars] + "... (truncated)"
    return text

def build_conversation_context(conversation_history):
    """
    Build a list of messages to send to OpenAI.
    - Starts with a system prompt that sets the bot's tone.
    - If the conversation history is too long, older messages are summarized.
    - Only the most recent user/assistant messages are kept in full.
    """
    system_prompt = {
        "role": "system",
        "content": (
            "You are a friendly, caring friend who is here to walk alongside you on your journey of "
            "understanding faith and Christianity. Just like a good friend, you are here to offer warm, "
            "personable explanations, making complex concepts simple and relatable. Whether the user is "
            "curious about the meaning of Easter, wondering what God is like, or exploring how faith impacts "
            "everyday life, you are here to help. Summarize answers in a warm, friendly manner using layman's "
            "terms, as if explaining to a friend. Let us keep it relatable and steer clear of impersonal phrases. "
            "We want our bot to reflect a Christian biblical worldview, emphasizing the love of God and the "
            "practical impact of faith. Focus on guiding users to understand Easter's meaning, what God is like, "
            "and how Christianity influences daily life. Instead of explaining things as divine justice or Christian "
            "faith and practice, let us talk from the perspective of a relationship with our loving Father in heaven. "
            "Christianity is not just stories; it is rooted in historical truth. Let us make users feel loved and cared for! "
            "You can vary the length of your answers, generally keeping them concise and readable so as not to overwhelm users, "
            "but if some questions are more complex and require more explanation, you can elaborate."
        )
    }
    
    max_history_length = 6  # Only keep the last 6 messages in full
    
    if len(conversation_history) > max_history_length:
        older_messages = conversation_history[:-max_history_length]
        recent_messages = conversation_history[-max_history_length:]
        older_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}" for msg in older_messages
        ])
        summary = summarize_text(older_text)
        context_message = {
            "role": "system",
            "content": f"Summary of earlier conversation:\n{summary}"
        }
        messages = [system_prompt, context_message] + recent_messages
    else:
        messages = [system_prompt] + conversation_history

    return messages

def chat_with_openai(conversation_history, user_input):
    """
    Appends the user input to the conversation history, builds the context,
    calls OpenAI's chat completion endpoint using the new API, and returns the assistant's
    reply along with the updated conversation history.
    """
    # Append the new user message
    conversation_history.append({"role": "user", "content": user_input})
    
    # Build messages including the system prompt, any necessary summary, and recent conversation
    messages = build_conversation_context(conversation_history)
    
    # Call the new OpenAI chat completion endpoint
    completion = client.chat.completions.create(
        model="gpt-4o",  # Change this to your desired model (e.g. "gpt-4o", "gpt-3.5-turbo-16k", etc.)
        messages=messages,
        max_tokens=512,
        temperature=0.7
    )
    
    # Extract the assistant's reply text from the response
    assistant_reply = completion.choices[0].message.content.replace("**", "").replace("*", "")
    conversation_history.append({"role": "assistant", "content": assistant_reply})
    
    return assistant_reply, conversation_history

@app.route("/", methods=["GET"])
def alive():
    return jsonify("alive"), 200

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Handles incoming JSON payloads from Kommunicate.
    - If eventName is "WELCOME", reply with welcome messages.
    - If the user's message contains human connection keywords, reply with a specific contact message.
    - Otherwise, process the message using conversation summarization and OpenAI.
    """
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "No JSON payload provided"}), 400

   # 1. Handle welcome events
    if payload.get("eventName") == "WELCOME":
        welcome_messages = [
            {
                "message": (
                    "🤖 Ask me about Easter 🐰🥚, why Christians 📖 ✝️ commemorate Easter, or any other questions you may have about exploring how faith impacts everyday life! "
                    "Feel free to ask anything! :D \n\nI may take a while to reply, please be patient with me! 🌻"
                ),
                "platform": "kommunicate",
                "metadata": {
                    "contentType": "300",
                    "templateId": "6",
                    "payload": [
                        {
                            "title": "What questions can I ask?",
                            "message": "What questions can I ask?"
                        },
                        {
                            "title": "Connect me to a human",
                            "message": "Connect me to a human"
                        }
                    ]
                }
            }
        ]
        return jsonify(welcome_messages), 200


    # 2. Check for human connection keywords in the user's message
    user_message = payload.get("message", "").lower()
    keywords = ["connect me to a human", "connect to human", "connect me to human", "talk to human"]
    if any(keyword in user_message for keyword in keywords):
        response_message = [
            {
                "message": "sure! you can drop us an email at digital@cru.org.sg!",
                "platform": "kommunicate",
            }
        ]
        return jsonify(response_message), 200
        
    # Within your webhook() function, after extracting user_message:
    user_message = payload.get("message", "").lower()

    # 2.1. Check if the message contains "what questions can i ask"
    if "what questions can i ask" in user_message:
        response_message = [
            {
                "message": (
                    "You can ask me questions like:\n\n"
                    "• If God is real, why He no make more obvious?\n"
                    "• Hasn’t science disproved Christianity?\n"
                    "• Don’t all good people go to heaven?\n"
                    "• Can we trust what the Bible says?\n"
                    "• Aren’t all religions just cults?\n"
                    "• Why does God allow suffering?\n"
                    "• How can we know God exists?\n"
                )
            }
        ]
        return jsonify(response_message), 200    
    
    # 3. For any other messages, process via OpenAI chat functionality.
    # Use the "from" field from the payload as the user ID (default to "default" if not provided)
    user_id = payload.get("from", "default")
    conversation_history = user_histories.get(user_id, [])

    try:
        reply, conversation_history = chat_with_openai(conversation_history, payload.get("message", ""))
    except Exception as e:
        return jsonify({"error": f"Error from OpenAI API: {str(e)}"}), 500

    # Update the user's conversation history
    user_histories[user_id] = conversation_history

    # Construct the answer as a list of dictionaries
    answer = [
        {
            "message": reply
        }
    ]

    # Return the reply (wrapped in a JSON object)
    return jsonify(answer), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
