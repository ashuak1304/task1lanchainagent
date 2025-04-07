import os
import json
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta

# Path to store credentials
CREDENTIALS_DIR = os.path.join(os.getcwd(), 'credentials')
if not os.path.exists(CREDENTIALS_DIR):
    os.makedirs(CREDENTIALS_DIR)

def save_credentials(credentials, user_id=None):
    """
    Save OAuth credentials to file or database
    
    Args:
        credentials: OAuth credentials object
        user_id: User ID (if None, a new ID will be generated)
        
    Returns:
        user_id: ID of the user whose credentials were saved
    """
    if user_id is None:
        # Generate a new user ID if none provided
        user_id = str(int(datetime.now().timestamp()))
    
    # Create user directory if it doesn't exist
    user_dir = os.path.join(CREDENTIALS_DIR, str(user_id))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    
    # Save credentials to file
    credentials_path = os.path.join(user_dir, 'credentials.json')
    
    # Convert credentials to JSON
    if hasattr(credentials, 'to_json'):
        credentials_json = credentials.to_json()
        with open(credentials_path, 'w') as f:
            f.write(credentials_json)
    else:
        # For non-Google credentials
        with open(credentials_path, 'wb') as f:
            pickle.dump(credentials, f)
    
    return user_id

def load_credentials(user_id):
    """
    Load OAuth credentials from file or database
    
    Args:
        user_id: User ID
        
    Returns:
        credentials: OAuth credentials object or None if not found
    """
    credentials_path = os.path.join(CREDENTIALS_DIR, str(user_id), 'credentials.json')
    
    if not os.path.exists(credentials_path):
        return None
    
    try:
        # Try to load as Google credentials
        with open(credentials_path, 'r') as f:
            credentials_json = f.read()
            credentials = Credentials.from_json(credentials_json)
            
            # Check if credentials are expired and refresh if possible
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                save_credentials(credentials, user_id)
            
            return credentials
    except:
        # Try to load as pickle (for non-Google credentials)
        try:
            with open(credentials_path, 'rb') as f:
                return pickle.load(f)
        except:
            return None

def create_oauth_flow(client_secrets_file, scopes, redirect_uri):
    """
    Create an OAuth flow for Google authentication
    
    Args:
        client_secrets_file: Path to client secrets JSON file
        scopes: List of OAuth scopes to request
        redirect_uri: Redirect URI for OAuth callback
        
    Returns:
        flow: OAuth flow object
    """
    return Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=scopes,
        redirect_uri=redirect_uri
    )

def revoke_credentials(credentials):
    """
    Revoke OAuth credentials
    
    Args:
        credentials: OAuth credentials object
        
    Returns:
        success: Boolean indicating if revocation was successful
    """
    if not credentials:
        return False
    
    try:
        import requests
        response = requests.post(
            'https://oauth2.googleapis.com/revoke',
            params={'token': credentials.token},
            headers={'content-type': 'application/x-www-form-urlencoded'}
        )
        return response.status_code == 200
    except:
        return False

def delete_credentials(user_id):
    """
    Delete stored credentials for a user
    
    Args:
        user_id: User ID
        
    Returns:
        success: Boolean indicating if deletion was successful
    """
    credentials_path = os.path.join(CREDENTIALS_DIR, str(user_id), 'credentials.json')
    
    if not os.path.exists(credentials_path):
        return False
    
    try:
        os.remove(credentials_path)
        return True
    except:
        return False
