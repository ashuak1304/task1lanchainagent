import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the scopes needed for your application
SCOPES = ["https://www.googleapis.com/auth/gmail.modify", 
          "https://www.googleapis.com/auth/calendar"]

def main():
    creds = None
    # Check if token.json already exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for future use
        with open("token.json", "w") as token:
            token.write(creds.to_json())
        print("Token successfully generated and saved to token.json")

if __name__ == "__main__":
    main()
