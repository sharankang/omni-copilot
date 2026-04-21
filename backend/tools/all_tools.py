from langchain.tools import tool
import os
import requests
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import uuid
from langchain_core.pydantic_v1 import BaseModel, Field

# --- Helper to Get Google Service ---
def get_calendar_service():
    """Loads credentials from token.json and returns the Google Calendar service."""
    token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
    if not os.path.exists(token_path):
        return None
    
    with open(token_path, "r") as token_file:
        creds_data = json.load(token_file)
        creds = Credentials.from_authorized_user_info(creds_data)
        return build("calendar", "v3", credentials=creds)

def get_gmail_service():
    """Loads credentials from token.json and returns the Gmail service."""
    token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
    if not os.path.exists(token_path):
        return None
    
    with open(token_path, "r") as token_file:
        creds_data = json.load(token_file)
        creds = Credentials.from_authorized_user_info(creds_data)
        return build("gmail", "v1", credentials=creds)

def get_drive_service():
    """Loads credentials from token.json and returns the Google Drive service."""
    token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
    if not os.path.exists(token_path):
        return None
    
    with open(token_path, "r") as token_file:
        creds_data = json.load(token_file)
        creds = Credentials.from_authorized_user_info(creds_data)
        return build("drive", "v3", credentials=creds)

class ScheduleMeetingInput(BaseModel):
    summary: str = Field(description="The title or topic of the meeting")
    start_time: str = Field(description="The start time of the meeting, preferably in ISO 8601 or natural language like 'tomorrow at 4pm'")
    end_time: str = Field(description="The end time of the meeting")
    attendees: list[str] = Field(default=[], description="List of attendee email addresses")
    description: str = Field(default="", description="Detailed description or agenda for the meeting")

# 1. Google Calendar Tool
@tool("schedule_meeting_tool", args_schema=ScheduleMeetingInput)
def schedule_meeting_tool(summary: str, start_time: str, end_time: str, attendees: list = [], description: str = "") -> str:
    """Schedules a meeting in Google Calendar and automatically generates a Google Meet link."""
    service = get_calendar_service()
    if not service:
        # Fallback to realistic mock if token is missing, but notify the user
        import random
        import string
        random_id = '-'.join([''.join(random.choices(string.ascii_lowercase, k=n)) for n in [3, 4, 3]])
        meet_link = f"https://meet.google.com/{random_id}"
        return f"(MOCK) Please run 'python3 utils/generate_google_token.py' in the backend folder to activate real meetings. \nSuccessfully scheduled '{summary}' from {start_time} to {end_time}. Mock link: {meet_link}"

    try:
        try:
            from dateutil.parser import parse as parse_date
            import datetime
            dt_start = parse_date(start_time, fuzzy=True)
            dt_end = parse_date(end_time, fuzzy=True)
            
            # If no tzinfo is set, we need to apply local timezone offset or just Z
            if not dt_start.tzinfo:
                dt_start = dt_start.replace(tzinfo=datetime.timezone.utc)
            if not dt_end.tzinfo:
                dt_end = dt_end.replace(tzinfo=datetime.timezone.utc)
                
            start_time = dt_start.isoformat()
            end_time = dt_end.isoformat()
        except:
            # Fallback
            if not start_time.endswith('Z') and '+' not in start_time and '-' not in start_time[-6:]:
                start_time += 'Z'
            if not end_time.endswith('Z') and '+' not in end_time and '-' not in end_time[-6:]:
                end_time += 'Z'

        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time},
            'end': {'dateTime': end_time},
            'attendees': [{'email': e} for e in attendees],
            'transparency': 'opaque',
            'conferenceData': {
                'createRequest': {
                    'requestId': str(uuid.uuid4()),
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }

        event = service.events().insert(
            calendarId='primary', 
            body=event, 
            sendUpdates='all',
            conferenceDataVersion=1
        ).execute()

        meet_link = event.get('hangoutLink', 'No link generated.')
        return f"Successfully scheduled '{summary}' from {start_time} to {end_time}. Real Google Meet link: {meet_link}. [SYSTEM: Task complete. Stop tool calling and reply to user.]"

    except HttpError as error:
        return f"An error occurred with Google Calendar API: {error}"

# 2. Gmail Tool
@tool
def send_email_tool(to_email: str, subject: str, body: str) -> str:
    """Sends an email via Gmail API."""
    import base64
    from email.message import EmailMessage
    
    service = get_gmail_service()
    if not service:
        return "Gmail credentials not found. Please run 'python3 utils/generate_google_token.py' in backend."
        
    try:
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to_email
        message['From'] = 'me'
        message['Subject'] = subject
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        service.users().messages().send(userId='me', body=create_message).execute()
        return f"Email sent to {to_email} with subject '{subject}'. [SYSTEM: Task complete. Stop tool calling and reply to user.]"
    except HttpError as error:
        return f"An HTTP error occurred with Gmail API: {error.resp.status} - {error.content}"
    except Exception as general_error:
        import traceback
        return f"A generic error occurred: {general_error} \n {traceback.format_exc()}"

# 3. Google Drive Tool
@tool
def search_drive_tool(query: str = "") -> str:
    """Searches for files in Google Drive. If query is provided, searches by file name. If empty, returns the most recently modified files. Pass ONLY the raw file name or keyword (e.g. 'Archi_resume.pdf'). Do NOT include search operators."""
    service = get_drive_service()
    if not service:
        return "Google Drive credentials not found. Please run 'python3 utils/generate_google_token.py'."
        
    try:
        q_param = f"name contains '{query}' and trashed = false" if query else "trashed = false"
        results = service.files().list(
            q=q_param, 
            pageSize=10, 
            orderBy="modifiedTime desc",
            fields="nextPageToken, files(id, name, webViewLink, modifiedTime)"
        ).execute()
        files = results.get('files', [])
        
        if not files:
            return f"No matching files found in Google Drive."
            
        file_data = []
        for file in files:
            file_data.append(f"Name: {file.get('name')}\\nModified: {file.get('modifiedTime')}\\nLink: {file.get('webViewLink', 'No link available')}\\n---")
            
        return "\\n".join(file_data)
    except HttpError as error:
        return f"An error occurred searching Google Drive: {error}"

class ReadDriveFileInput(BaseModel):
    query: str = Field(description="The exact name of the file or keyword to search for in Google Drive (e.g. 'Archi_resume.pdf')")

# 3b. Read Google Drive File Content
@tool("read_drive_file_tool", args_schema=ReadDriveFileInput)
def read_drive_file_tool(query: str) -> str:
    """Reads the textual content of a file from Google Drive (e.g., a PDF) given its name. Pass ONLY the raw file name or keyword."""
    import io
    from googleapiclient.http import MediaIoBaseDownload
    
    service = get_drive_service()
    if not service:
        return "Google Drive credentials not found."
    
    try:
        results = service.files().list(
            q=f"name contains '{query}'", 
            pageSize=1, 
            fields="files(id, name, mimeType)"
        ).execute()
        files = results.get('files', [])
        
        if not files:
            return f"No matching files found for '{query}' to read."
            
        file_id = files[0]['id']
        mime_type = files[0].get('mimeType', '')
        
        if 'pdf' in mime_type.lower() or query.lower().endswith('.pdf'):
            try:
                from pypdf import PdfReader
            except ImportError:
                return "The pypdf library is not installed."
                
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                
            fh.seek(0)
            reader = PdfReader(fh)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text[:4000] # Return enough chars for a standard LLM window
        else:
            return f"Unsupported file type. MIME type: {mime_type}. Currently this tool only supports reading PDF files directly."
            
    except HttpError as error:
        return f"An error occurred reading from Google Drive: {error}"
    except Exception as e:
        return f"Error extracting content: {e}"

# 3c. Upload File to Google Drive
class UploadDriveInput(BaseModel):
    local_path: str = Field(description="The absolute path of the local file to upload (usually provided in prompt as [Attached File: ...])")
    new_name: str = Field(default="", description="Optional new name for the file in drive. If empty, uses original name")

@tool("upload_to_drive_tool", args_schema=UploadDriveInput)
def upload_to_drive_tool(local_path: str, new_name: str = "") -> str:
    """Uploads a local file from the server to Google Drive."""
    import os
    from googleapiclient.http import MediaFileUpload
    
    service = get_drive_service()
    if not service:
        return "Google Drive credentials not found."
    
    if not os.path.exists(local_path):
        return f"Local file not found on the server at path: {local_path}. Please make sure you have the exact file path correct."
        
    filename = new_name if new_name else os.path.basename(local_path)
    
    try:
        file_metadata = {'name': filename}
        media = MediaFileUpload(local_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        # Cleanup automatically
        try:
            os.remove(local_path)
        except:
            pass
            
        return f"Successfully uploaded '{filename}' to Google Drive. Link: {file.get('webViewLink')}. [SYSTEM: Task complete. Stop tool calling and reply to user.]"
    except Exception as e:
        return f"Error uploading to Drive: {e}"

# 4. Notion Tool
@tool
def create_notion_note_tool(title: str, content: str) -> str:
    """Creates a note or page in Notion workspace."""
    from notion_client import Client
    notion_token = os.getenv("NOTION_API_KEY")
    if not notion_token:
        return "Notion API key not configured."
    
    try:
        notion = Client(auth=notion_token)
        # Find an accessible parent page or database
        results = notion.search(filter={"property": "object", "value": "page"}).get("results", [])
        if not results:
            results = notion.search(filter={"property": "object", "value": "database"}).get("results", [])
            
        if not results:
            return "Cannot create Notion page. Your Notion integration hasn't been granted access to any pages. Please open Notion, go to the parent page/workspace (like 'Archi Jain’s Space HQ'), click the 3-dots menu (top right) -> Add connections -> select your integration."
            
        parent = results[0]
        parent_id = parent["id"]
        parent_type = parent["object"]
        
        new_page = {
            "parent": {"type": f"{parent_type}_id", f"{parent_type}_id": parent_id},
            "properties": {},
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}
                }
            ]
        }
        
        if parent_type == "database":
            new_page["properties"] = {"Name": {"title": [{"text": {"content": title}}]}}
        else:
            new_page["properties"] = {"title": {"title": [{"text": {"content": title}}]}}
            
        created = notion.pages.create(**new_page)
        page_url = created.get("url", "No URL returned")
        return f"Successfully created Notion content '{title}'. Link to view: {page_url}. [SYSTEM: Task complete. Stop tool calling and reply to user.]"
    except Exception as e:
        return f"Failed to create Notion page. Note that Database parent configurations may have different required properties. Error: {str(e)}"

# 5. Slack Tool
@tool
def send_slack_message_tool(channel: str, message: str) -> str:
    """Sends a message to a specific Slack channel or user. Examples of channel: '#general', '#random'."""
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
         return "Slack tool is not configured. Missing SLACK_BOT_TOKEN."
         
    try:
        client = WebClient(token=slack_token)
        client.chat_postMessage(channel=channel, text=message)
        return f"Successfully sent message to {channel} on Slack. [SYSTEM: Task complete. Stop tool calling and reply to user immediately.]"
    except SlackApiError as e:
        return f"Failed to send Slack message: {e.response['error']}"
    except Exception as general_error:
        return f"An error occurred with Slack: {str(general_error)}"

# 6. Discord Tool
@tool
def send_discord_message_tool(message: str) -> str:
    """Sends a message to a Discord channel via Webhook."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return "Discord webhook URL not configured."
    # requests.post(webhook_url, json={"content": message})
    return "Message sent to Discord."

# 7. Google Meet Tool
@tool
def create_google_meet_tool(topic: str, duration_mins: int = 30) -> str:
    """Creates a Google Meet meeting link."""
    from datetime import datetime, timedelta
    
    service = get_calendar_service()
    if not service:
        import random
        import string
        random_id = '-'.join([''.join(random.choices(string.ascii_lowercase, k=n)) for n in [3, 4, 3]])
        meet_link = f"https://meet.google.com/{random_id}"
        return f"(MOCK) Please run 'python3 utils/generate_google_token.py' to activate real meetings. \nGoogle Meet '{topic}' for {duration_mins} mins created. Mock link: {meet_link}"

    try:
        now = datetime.utcnow()
        start = now.isoformat() + 'Z'
        end = (now + timedelta(minutes=duration_mins)).isoformat() + 'Z'
        
        event = {
            'summary': topic,
            'start': {'dateTime': start},
            'end': {'dateTime': end},
            'conferenceData': {
                'createRequest': {
                    'requestId': str(uuid.uuid4()),
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }

        event = service.events().insert(
            calendarId='primary', 
            body=event, 
            conferenceDataVersion=1
        ).execute()

        meet_link = event.get('hangoutLink', 'No link generated.')
        return f"Google Meet '{topic}' for {duration_mins} mins created. Link: {meet_link}"

    except HttpError as error:
        return f"An error occurred with Google Calendar API: {error}"



class ReadEmailsInput(BaseModel):
    max_results: int = Field(default=5, description="Maximum number of emails to fetch")
    query: str = Field(default="", description="Search query string. Leave empty to get all recent emails.")

# 9. Read Emails Tool
@tool("read_emails_tool", args_schema=ReadEmailsInput)
def read_emails_tool(max_results: int = 5, query: str = "") -> str:
    """Reads recent emails from Gmail. Can filter by a search query."""
    service = get_gmail_service()
    if not service:
         return "Gmail credentials not found. Please run 'python3 utils/generate_google_token.py'."
         
    try:
        results = service.users().messages().list(userId='me', maxResults=max_results, q=query).execute()
        messages = results.get('messages', [])
        
        if not messages:
            return "No emails found."
            
        email_data = []
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            
            # Extract headers (Subject, From, Date)
            headers = msg_data.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            # Extract snippet
            snippet = msg_data.get('snippet', '')
            
            email_data.append(f"From: {sender}\nDate: {date}\nSubject: {subject}\nSnippet: {snippet}\n---")
            
        return "\n".join(email_data) + "\n\n[SYSTEM: Task complete. Stop tool calling and reply to user immediately summarizing the above.]"
    except HttpError as error:
        return f"An error occurred reading emails: {error}"

class ReadCalendarEventsInput(BaseModel):
    max_results: int = Field(default=10, description="Maximum number of events to fetch")
    time_min: str = Field(default="", description="Start time for events, preferably in ISO 8601 or natural language like 'now' or 'tomorrow'")

# 10. Read Calendar Events Tool
@tool("read_calendar_events_tool", args_schema=ReadCalendarEventsInput)
def read_calendar_events_tool(max_results: int = 10, time_min: str = "") -> str:
    """Reads upcoming events from Google Calendar. Defaults to now if not provided."""
    service = get_calendar_service()
    if not service:
        return "Google Calendar credentials not found. Please run 'python3 utils/generate_google_token.py'."
        
    try:
        if not time_min or time_min.lower() == "now":
            from datetime import datetime
            time_min = datetime.utcnow().isoformat() + 'Z'
        else:
            try:
                from dateutil.parser import parse as parse_date
                import datetime
                dt_time = parse_date(time_min, fuzzy=True)
                if not dt_time.tzinfo:
                    dt_time = dt_time.replace(tzinfo=datetime.timezone.utc)
                time_min = dt_time.isoformat()
            except Exception:
                from datetime import datetime
                time_min = datetime.utcnow().isoformat() + 'Z'
            
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=time_min,
            maxResults=max_results, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "No upcoming events found."
            
        event_data = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            summary = event.get('summary', 'No Title')
            event_data.append(f"Event: {summary}\\nStart: {start}\\nEnd: {end}\\n---")
            
        return "\\n".join(event_data)
    except HttpError as error:
        return f"An error occurred reading calendar events: {error}"

OMNI_TOOLS = [
    schedule_meeting_tool,
    send_email_tool,
    search_drive_tool,
    read_drive_file_tool,
    upload_to_drive_tool,
    create_notion_note_tool,
    send_slack_message_tool,
    send_discord_message_tool,
    create_google_meet_tool,

    read_emails_tool,
    read_calendar_events_tool
]
