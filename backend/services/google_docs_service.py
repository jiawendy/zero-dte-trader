import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive.file']

def get_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("credentials.json not found. Please download it from Google Cloud Console.")
                
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return creds

def find_daily_doc(service, title):
    """Finds a file with the exact title in Drive."""
    try:
        # drive.file scope allows access to files created by this app
        # We search for non-trashed files with the exact name
        query = f"name = '{title}' and trashed = false and mimeType = 'application/vnd.google-apps.document'"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']
        return None
    except Exception as e:
        print(f"Error searching for doc: {e}")
        return None

def append_or_create_analysis_doc(title, content):
    """Creates a new Google Doc or appends to existing one for the day."""
    try:
        creds = get_credentials()
        docs_service = build('docs', 'v1', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)

        # Check if doc exists
        document_id = find_daily_doc(drive_service, title)
        
        if not document_id:
            # Create new document
            body = {'title': title}
            doc = docs_service.documents().create(body=body).execute()
            document_id = doc.get('documentId')
            print(f"Created new doc: {document_id}")
            
            # Insert initial content
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': content + "\n\n"
                    }
                }
            ]
        else:
            print(f"Found existing doc: {document_id}")
            # Get document bounds to append to the end
            doc = docs_service.documents().get(documentId=document_id).execute()
            content_len = doc.get('body').get('content')[-1].get('endIndex')
            
            # Append content with a separator
            requests = [
                {
                    'insertText': {
                        'location': {'index': content_len - 1},
                        'text': "\n" + "-"*20 + "\n\n" + content + "\n"
                    }
                }
            ]
        
        docs_service.documents().batchUpdate(
            documentId=document_id, body={'requests': requests}).execute()
            
        return f"https://docs.google.com/document/d/{document_id}/edit"
        
    except Exception as e:
        print(f"Error handling doc: {e}")
        raise e
