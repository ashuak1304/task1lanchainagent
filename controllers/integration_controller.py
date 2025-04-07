from flask import Blueprint, request, render_template, redirect, url_for, session, flash, jsonify
from services.search_service import SearchService
from services.slack_service import SlackService
from services.calendar_service import CalendarService
from utils.auth_utils import load_credentials
import json

# Create blueprint
integration_bp = Blueprint('integration', __name__, url_prefix='/integration')

# Initialize services
search_service = SearchService()
slack_service = SlackService()
calendar_service = CalendarService()

@integration_bp.route('/search', methods=['GET', 'POST'])
def search():
    """Web search integration"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        query = request.form.get('query')
        
        # Perform web search
        results = search_service.search_web(query)
        
        return render_template('integration/search_results.html', 
                              results=results,
                              query=query)
    
    return render_template('integration/search.html')

@integration_bp.route('/slack/connect', methods=['GET', 'POST'])
def slack_connect():
    """Connect to Slack"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        workspace = request.form.get('workspace')
        channel = request.form.get('channel')
        token = request.form.get('token')
        
        # Save Slack configuration
        success = slack_service.configure(user_id, workspace, channel, token)
        
        if success:
            flash('Slack integration configured successfully', 'success')
            return redirect(url_for('integration.settings'))
        else:
            flash('Failed to configure Slack integration', 'error')
    
    return render_template('integration/slack_connect.html')

@integration_bp.route('/slack/send', methods=['POST'])
def slack_send():
    """Send message to Slack"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    data = request.get_json()
    message = data.get('message')
    channel = data.get('channel')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Send message to Slack
    success = slack_service.send_message(message, channel)
    
    if success:
        return jsonify({'status': 'success'})
    else:
        return jsonify({'error': 'Failed to send message to Slack'}), 500

@integration_bp.route('/calendar/connect', methods=['GET', 'POST'])
def calendar_connect():
    """Connect to Google Calendar"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        # Calendar connection is handled through Google OAuth
        # This is just a placeholder for additional calendar settings
        primary_calendar = request.form.get('primary_calendar')
        
        # Save calendar configuration
        success = calendar_service.configure(user_id, primary_calendar)
        
        if success:
            flash('Calendar integration configured successfully', 'success')
            return redirect(url_for('integration.settings'))
        else:
            flash('Failed to configure calendar integration', 'error')
    
    return render_template('integration/calendar_connect.html')

@integration_bp.route('/calendar/create', methods=['POST'])
def calendar_create():
    """Create calendar event"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    data = request.get_json()
    event = data.get('event')
    
    if not event:
        return jsonify({'error': 'Event details are required'}), 400
    
    # Create calendar event
    success, event_id = calendar_service.create_event(user_id, event)
    
    if success:
        return jsonify({'status': 'success', 'event_id': event_id})
    else:
        return jsonify({'error': 'Failed to create calendar event'}), 500

@integration_bp.route('/settings')
def settings():
    """Integration settings page"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    # Get current integration settings
    slack_config = slack_service.get_configuration(user_id)
    calendar_config = calendar_service.get_configuration(user_id)
    
    return render_template('integration/settings.html',
                          slack_config=slack_config,
                          calendar_config=calendar_config)

@integration_bp.route('/test/<service>')
def test_integration(service):
    """Test integration connection"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    if service == 'slack':
        success = slack_service.test_connection(user_id)
        service_name = 'Slack'
    elif service == 'calendar':
        success = calendar_service.test_connection(user_id)
        service_name = 'Calendar'
    elif service == 'search':
        success = search_service.test_connection()
        service_name = 'Web Search'
    else:
        flash(f'Unknown service: {service}', 'error')
        return redirect(url_for('integration.settings'))
    
    if success:
        flash(f'{service_name} integration is working correctly', 'success')
    else:
        flash(f'{service_name} integration test failed', 'error')
    
    return redirect(url_for('integration.settings'))
