from flask import Blueprint, request, redirect, url_for, render_template, session, flash
import os
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from services.email_service import EmailService
from utils.auth_utils import save_credentials, load_credentials

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Google OAuth configuration
CLIENT_SECRETS_FILE = os.path.join(os.getcwd(), 'config', 'credentials.json')
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/calendar']
REDIRECT_URI = 'http://localhost:5000/auth/callback'

@auth_bp.route('/login')
def login():
    """Render login page"""
    return render_template('auth/login.html')

@auth_bp.route('/google')
def google_auth():
    """Initiate Google OAuth flow"""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    session['state'] = state
    return redirect(authorization_url)

@auth_bp.route('/callback')
def callback():
    """Handle OAuth callback"""
    state = session.get('state')
    
    if not state or state != request.args.get('state'):
        flash('Authentication failed: State mismatch', 'error')
        return redirect(url_for('auth.login'))
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state=state
    )
    
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    
    # Save credentials for later use
    user_id = save_credentials(credentials)
    session['user_id'] = user_id
    
    # Initialize email service with user credentials
    email_service = EmailService()
    email_service.initialize_for_user(user_id)
    
    flash('Successfully authenticated with Google', 'success')
    return redirect(url_for('email.inbox'))

@auth_bp.route('/logout')
def logout():
    """Log out user"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/settings')
def settings():
    """Render authentication settings page"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('auth/settings.html')

@auth_bp.route('/revoke')
def revoke():
    """Revoke OAuth access"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    credentials = load_credentials(user_id)
    
    if credentials:
        revoke = requests.post('https://oauth2.googleapis.com/revoke',
            params={'token': credentials.token},
            headers={'content-type': 'application/x-www-form-urlencoded'})
        
        # Clear stored credentials
        # Implementation depends on your storage method
        
        session.clear()
        flash('Access successfully revoked', 'success')
    
    return redirect(url_for('auth.login'))
