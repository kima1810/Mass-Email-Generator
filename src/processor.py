import time
import pandas as pd
from googleapiclient.errors import HttpError

from .auth import authenticate_gmail, get_gmail_signature
from .drafts import create_draft_with_retry, create_message
from .formatting import personalize_template


def process_contacts(csv_path, subject, template, include_signature):
    service = authenticate_gmail()
    gmail_signature = get_gmail_signature(service) if include_signature else ''
    df = pd.read_csv(csv_path)

    if 'email' not in df.columns or 'first_name' not in df.columns:
        raise ValueError("CSV must contain 'email' and 'first_name' columns")

    draft_count = 0
    failed_drafts = []
    total_contacts = len(df)

    for _, row in df.iterrows():
        first_name = row['first_name']
        email = row['email']

        if pd.isna(first_name):
            failed_drafts.append(email)
            continue

        try:
            personalized_body = personalize_template(template, first_name)
            if gmail_signature:
                personalized_body += f"\n\n{gmail_signature}"

            message = create_message(email, subject, personalized_body)
            create_draft_with_retry(service, 'me', message)
            draft_count += 1
            print(f"Draft {draft_count}/{total_contacts} created for {email}")
            time.sleep(0.5)

        except HttpError as error:
            print(f"Failed to create draft for {email}: {str(error)}")
            failed_drafts.append(email)
            continue
        except Exception as error:
            print(f"Unexpected error for {email}: {str(error)}")
            failed_drafts.append(email)
            continue

    return draft_count, failed_drafts
