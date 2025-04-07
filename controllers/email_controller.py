from flask import Blueprint, request, render_template, redirect, url_for, session, flash, jsonify
from services.email_service import EmailService
from services.llm_service import LLMService
from services.search_service import SearchService
from services.slack_service import SlackService
from services.calendar_service import CalendarService
from utils.auth_utils import load_credentials
from utils.parser_utils import parse_email_content
import json

# Create blueprint
email_bp = Blueprint('email', __name__, url_prefix='/email')

# Initialize services
email_service = EmailService()
llm_service = LLMService()
search_service = SearchService()
slack_service = SlackService()
calendar_service = CalendarService()

@email_bp.route('/inbox')
def inbox():
    """Display user's inbox"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    credentials = load_credentials(user_id)
    
    if not credentials:
        flash('Authentication required', 'error')
        return redirect(url_for('auth.login'))
    
    # Fetch emails from Gmail
    emails = email_service.get_inbox(user_id)
    
    return render_template('email/inbox.html', emails=emails)

@email_bp.route('/view/<email_id>')
def view_email(email_id):
    """View a specific email"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    # Fetch the specific email
    email = email_service.get_email(user_id, email_id)
    
    if not email:
        flash('Email not found', 'error')
        return redirect(url_for('email.inbox'))
    
    # Use LLM to understand email context
    email_context = llm_service.analyze_email(email)
    
    return render_template('email/view.html', email=email, context=email_context)

@email_bp.route('/compose', methods=['GET', 'POST'])
def compose():
    """Compose a new email"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        to = request.form.get('to')
        subject = request.form.get('subject')
        body = request.form.get('body')
        
        user_id = session['user_id']
        
        # Send the email
        success = email_service.send_email(user_id, to, subject, body)
        
        if success:
            flash('Email sent successfully', 'success')
            return redirect(url_for('email.inbox'))
        else:
            flash('Failed to send email', 'error')
    
    return render_template('email/compose.html')

@email_bp.route('/reply/<email_id>', methods=['GET', 'POST'])
def reply(email_id):
    """Reply to an email"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    # Fetch the original email
    email = email_service.get_email(user_id, email_id)
    
    if not email:
        flash('Email not found', 'error')
        return redirect(url_for('email.inbox'))
    
    if request.method == 'POST':
        body = request.form.get('body')
        
        # Send the reply
        success = email_service.reply_to_email(user_id, email_id, body)
        
        if success:
            flash('Reply sent successfully', 'success')
            return redirect(url_for('email.inbox'))
        else:
            flash('Failed to send reply', 'error')
    
    # Generate AI suggested reply
    suggested_reply = llm_service.generate_reply(email)
    
    return render_template('email/reply.html', email=email, suggested_reply=suggested_reply)

@email_bp.route('/auto-reply/<email_id>')
def auto_reply(email_id):
    """Generate and send an automated reply"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    # Fetch the email
    email = email_service.get_email(user_id, email_id)
    
    if not email:
        flash('Email not found', 'error')
        return redirect(url_for('email.inbox'))
    
    # Generate AI reply
    reply_text = llm_service.generate_reply(email)
    
    # Send the reply
    success = email_service.reply_to_email(user_id, email_id, reply_text)
    
    if success:
        flash('Auto-reply sent successfully', 'success')
    else:
        flash('Failed to send auto-reply', 'error')
    
    return redirect(url_for('email.view', email_id=email_id))

@email_bp.route('/search', methods=['GET', 'POST'])
def search():
    """Search emails and web for information"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        query = request.form.get('query')
        search_web = request.form.get('search_web') == 'on'
        
        user_id = session['user_id']
        
        # Search emails
        email_results = email_service.search_emails(user_id, query)
        
        # Search web if requested
        web_results = []
        if search_web:
            web_results = search_service.search_web(query)
        
        return render_template('email/search_results.html', 
                              email_results=email_results, 
                              web_results=web_results,
                              query=query)
    
    return render_template('email/search.html')

@email_bp.route('/calendar/<email_id>')
def create_calendar_event(email_id):
    """Extract calendar event from email and create it"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    # Fetch the email
    email = email_service.get_email(user_id, email_id)
    
    if not email:
        flash('Email not found', 'error')
        return redirect(url_for('email.inbox'))
    
    # Extract event details using LLM
    event_details = llm_service.extract_event_details(email)
    
    if not event_details:
        flash('No event details found in this email', 'warning')
        return redirect(url_for('email.view', email_id=email_id))
    
    # Create calendar event
    success = calendar_service.create_event(user_id, event_details)
    
    if success:
        flash('Calendar event created successfully', 'success')
    else:
        flash('Failed to create calendar event', 'error')
    
    return redirect(url_for('email.view', email_id=email_id))

@email_bp.route('/slack/<email_id>')
def send_to_slack(email_id):
    """Send email content to Slack"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    # Fetch the email
    email = email_service.get_email(user_id, email_id)
    
    if not email:
        flash('Email not found', 'error')
        return redirect(url_for('email.inbox'))
    
    # Format email for Slack
    email_summary = llm_service.summarize_email(email)
    
    # Send to Slack
    success = slack_service.send_message(email_summary)
    
    if success:
        flash('Email sent to Slack successfully', 'success')
    else:
        flash('Failed to send to Slack', 'error')
    
    return redirect(url_for('email.view', email_id=email_id))

@email_bp.route('/api/emails', methods=['GET'])
def api_get_emails():
    """API endpoint to get emails"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    # Fetch emails
    emails = email_service.get_inbox(user_id)
    
    return jsonify({'emails': emails})

@email_bp.route('/api/email/<email_id>', methods=['GET'])
def api_get_email(email_id):
    """API endpoint to get a specific email"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    # Fetch the email
    email = email_service.get_email(user_id, email_id)
    
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    return jsonify({'email': email})
