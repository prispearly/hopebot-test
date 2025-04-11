# ✝️ Family Life Bot 
```
keep_alive.py
```

A Flask-based backend for a faith-oriented chatbot system that integrates:

- 🧠 **OpenAI GPT-3.5** for natural language understanding  
- 📅 **Google Sheets scraping** for dynamic event data  
- 📬 **Email notifications** via SMTP  
- 🤖 **Kommunicate webhook** support  
- 🔗 Deployed with Flask & CORS, with threading support via `keep_alive()`

---

## 🚀 Features

- Responds to Telegram or Kommunicate webhook queries using OpenAI
- Parses and matches user questions to upcoming Christian events from Google Sheets
- Sends email notifications for small group sign-up requests
- Scrapes Google Sheets published pages to extract content dynamically
- Secure with `.env` for API keys and email credentials

---

## 📁 Project Structure

```
.
├── keep_alive.py               # Flask thread runner
├── fetch_frm_gsheets.py        # Google Sheets scraping helpers
├── monthly_webscrape_and_write_to_gsheets.py  # Scheduled scraping logic
├── write_data_to_sheet
├── clean_and_return_title
├── .env                        # Environment variables (not included)
```

---

## 🔐 Environment Setup (`.env` file)

```env
tg_token=XXX
ai_token=XXX
google_api_key=api_key": "XXX"
email_address=XXX
email_password=XXX
```

---

## 📦 Requirements

Install dependencies:
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install flask flask-cors openai gspread beautifulsoup4 python-dotenv
```

---

## 🧠 GPT Role Configuration

System prompt is carefully crafted to reflect a warm, friendly Christian companion:

- Explains Easter, God, and Christian faith in **layman's terms**
- Based on a **relational biblical worldview**
- Keeps responses **short, warm, and practical**

---

## 📡 API Endpoints

### `/`
**GET**  
Health check — returns `"Alive"`.

---

### `/gformsubmit`
**POST**  
Triggers a full scrape of registered URLs via `monthly_webscrape_and_write_to_gsheets`.

---

### `/join-small-grp-request`
**POST**  
Receives form submissions (from Kommunicate). Sends email notifications for small group sign-ups.

**Request body example:**
```json
{
  "Name": "Jane",
  "Phone": "+6591234567",
  "Email": "jane@example.com",
  "Ministry Type": "Parenting"
}
```

---

### `/webhook`
**POST**  
Handles Kommunicate webhook messages. Extracts message text, calls GPT-3.5 with a faith-based system role, and returns an AI-generated response.

---

### `/event`
**POST**  
Matches user questions to events scraped from a Google Sheet.

**Flow:**
1. Extracts event titles from a published Google Sheet
2. Uses GPT-3.5 to match the user query with the most relevant event
3. Retrieves detailed info from the selected event row
4. Uses GPT-3.5 again to generate a short answer (<50 words) about the event

---

### `/test`
**POST**  
A basic test endpoint that scrapes a hardcoded Google Sheet and returns a sample event-related cell.

---

## 📤 Email Integration

Uses `smtplib` to send email from a Gmail account. Ensure you use an **App Password**, not your main Gmail password.

---

## 🧵 Threaded App Execution

To allow persistent background running:
```python
if __name__ == '__main__':
    keep_alive()
```

---

## 📝 Notes

- Web scraping is done on **published** Google Sheets.
- GPT-3.5 is used in **multiple roles** (categorization and content response).
- Email responses are configured for **ministry sign-up** scenarios.
- Consider adding session or user tracking for more personalized GPT context.

---

## 🙏 Example Queries

- “When is the next Art of Marriage retreat?”
- “How can I sign up for HomeBuilders group?”
- “What topics are covered in the upcoming parenting event?”

---

## 📜 License

MIT License. Free to use and modify.

---

Let me know if you'd like a `requirements.txt` or deployment script next!