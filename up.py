


import os
import pickle
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# הגדרת הסקופים הדרושים
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate_youtube():
    creds = None
    # קובץ הטוקן שנשמר לאחר ההתחברות הראשונית
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # אם אין טוקן או הוא לא תקף, מתחילים תהליך התחברות
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # שמירת הטוקן להבא
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)

def upload_video(youtube, file_path, title, description, tags, category_id, privacy_status):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"התקדמות: {int(status.progress() * 100)}%")

    print("הסרטון הועלה בהצלחה! מזהה הסרטון:", response.get("id"))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("שימוש: python upload_video.py <נתיב לסרטון>")
        sys.exit(1)

    file_path = sys.argv[1]
    youtube = authenticate_youtube()

    # פרטי הסרטון
    title = "כותרת הסרטון שלך"
    description = "תיאור הסרטון שלך"
    tags = ["תג1", "תג2", "תג3"]
    category_id = "22"  # קטגוריית אנשים ובלוגים
    privacy_status = "private"  # אפשרויות: "public", "unlisted", "private"

    upload_video(youtube, file_path, title, description, tags, category_id, privacy_status)
