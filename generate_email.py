import os
import sys
import base64
import re
import time
import pandas as pd
import webbrowser
from pathlib import Path
from tkinter import Tk, Label, Entry, Button, filedialog, Text, Checkbutton, IntVar, messagebox
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_token_path():
    """Get path for token.json in user's home directory"""
    # Use user's home directory which is always writable
    home_dir = Path.home()
    app_dir = home_dir / '.email_draft_generator'
    app_dir.mkdir(exist_ok=True)
    return str(app_dir / 'token.json')

# Backend
def authenticate_gmail():
    creds = None
    token_path = get_token_path()
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        try:
            flow = InstalledAppFlow.from_client_secrets_file(resource_path('credentials.json'), SCOPES)
            
            # Register a custom handler to explicitly open browser
            def open_browser(url):
                webbrowser.open(url, new=1)
                return True
            
            # Run the OAuth flow with explicit browser opening
            creds = flow.run_local_server(
                port=0,
                open_browser=True,
                success_message='Authentication successful! You can close this window and return to the application.',
                timeout_seconds=120
            )
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
                
        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}\n\nPlease ensure:\n1. Your default browser is set\n2. You have internet connection\n3. Firewall is not blocking the connection")
    
    return build('gmail', 'v1', credentials=creds)

def convert_markdown_to_html(text):
    """Convert markdown-style formatting to HTML"""
    # Bold: **text** or __text__
    text = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)
    
    # Italic: *text* or _text_
    text = re.sub(r'\*([^\*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)
    
    # Underline: ~~text~~
    text = re.sub(r'~~([^~]+)~~', r'<u>\1</u>', text)
    
    # Colored text: {color:text}
    # Supports common colors like red, blue, green, etc.
    text = re.sub(r'\{([a-zA-Z]+):([^\}]+)\}', r'<span style="color:\1">\2</span>', text)
    
    # Links: [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)
    
    return text

def text_to_html(text):
    """Convert plain text to HTML, preserving formatting"""
    # Convert markdown formatting
    html_text = convert_markdown_to_html(text)
    # Replace newlines with <br> tags
    html_text = html_text.replace('\n', '<br>')
    return html_text

def create_message(to, subject, body_text):
    # Convert plain text with markdown links to HTML
    html_body = text_to_html(body_text)
    message = MIMEText(html_body, 'html')
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'message': {'raw': raw}}

def create_draft(service, user_id, message_body):
    return service.users().drafts().create(userId=user_id, body=message_body).execute()

def create_draft_with_retry(service, user_id, message_body, max_retries=3):
    """Create draft with retry logic for rate limiting"""
    for attempt in range(max_retries):
        try:
            return service.users().drafts().create(userId=user_id, body=message_body).execute()
        except HttpError as e:
            if e.resp.status in [429, 500, 502, 503]:  # Rate limit or server errors
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    print(f"Rate limit hit, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise  # Re-raise if all retries failed
            else:
                raise  # Re-raise for other errors
        except Exception as e:
            raise  # Re-raise non-HTTP errors

def personalize_template(template, first_name):
    # Convert first_name to string to handle numeric values in CSV
    return template.replace('{{first_name}}', str(first_name))

def get_gmail_signature(service):
    try:
        profile = service.users().settings().sendAs().list(userId='me').execute()
        primary = next((item for item in profile['sendAs'] if item.get('isPrimary')), None)
        return primary.get('signature', '') if primary else ''
    except Exception as e:
        # If signature retrieval fails, just return empty string
        print(f"Could not retrieve signature: {str(e)}")
        return ''

def process_csv():
    subject = subject_entry.get()
    template = template_box.get("1.0", "end-1c")
    include_signature = signature.get()
    csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not csv_path or not subject or not template:
        messagebox.showwarning("Missing Input", "Please fill in subject and template, then select a CSV file")
        return

    try:
        # Show authentication message if needed
        token_path = get_token_path()
        if not os.path.exists(token_path):
            messagebox.showinfo("Authentication Required", "You will now be redirected to your browser to login with Google.\n\nPlease complete the authentication and return to this application.")
        
        service = authenticate_gmail()
        gmail_signature = get_gmail_signature(service) if include_signature else ''
        df = pd.read_csv(csv_path)
        
        # Validate required columns exist
        if 'email' not in df.columns or 'first_name' not in df.columns:
            messagebox.showerror("Error", "CSV must contain 'email' and 'first_name' columns")
            return

        draft_count = 0
        failed_drafts = []
        total_contacts = len(df)
        
        for index, row in df.iterrows():
            # Handle NaN or numeric values by converting to string and checking
            first_name = row['first_name']
            if pd.isna(first_name):
                messagebox.showerror("Error", f"Missing first_name for {row['email']}")
                failed_drafts.append(row['email'])
                continue
            
            try:
                personalized_body = personalize_template(template, first_name)
                if gmail_signature:
                    personalized_body += f"\n\n{gmail_signature}"
                message = create_message(row['email'], subject, personalized_body)
                
                # Use retry logic for draft creation
                create_draft_with_retry(service, 'me', message)
                draft_count += 1
                print(f"Draft {draft_count}/{total_contacts} created for {row['email']}")
                
                # Add small delay to avoid rate limiting (0.5 seconds)
                time.sleep(0.5)
                
            except HttpError as e:
                error_msg = f"Failed to create draft for {row['email']}: {str(e)}"
                print(error_msg)
                failed_drafts.append(row['email'])
                continue
            except Exception as e:
                error_msg = f"Unexpected error for {row['email']}: {str(e)}"
                print(error_msg)
                failed_drafts.append(row['email'])
                continue
        
        # Show results
        if failed_drafts:
            failed_list = '\n'.join(failed_drafts[:10])  # Show first 10
            if len(failed_drafts) > 10:
                failed_list += f"\n... and {len(failed_drafts) - 10} more"
            messagebox.showwarning("Partially Complete", 
                f"Created {draft_count} drafts successfully.\n\n"
                f"Failed to create {len(failed_drafts)} drafts:\n{failed_list}")
        else:
            messagebox.showinfo("Success", f"Successfully created {draft_count} email drafts in your Gmail!")
        
    except FileNotFoundError:
        messagebox.showerror("Error", "credentials.json file not found")
    except pd.errors.EmptyDataError:
        messagebox.showerror("Error", "CSV file is empty")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Frontend GUI
root = Tk()
root.title("Email Automation Assist")

Label(root, text="Subject:").pack()
subject_entry = Entry(root, width=50)
subject_entry.pack()

Label(root, text="Template (use {{first_name}}):").pack()
template_box = Text(root, height=10, width=50)
template_box.pack()

signature = IntVar()
Checkbutton(root, text="Include Signature", variable=signature).pack()

Button(root, text="Create Drafts", command=process_csv).pack()

root.mainloop()
