from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from dotenv import load_dotenv
from controllers.auth_controller import auth_bp
from controllers.email_controller import email_bp
from controllers.integration_controller import integration_bp
from services.email_service import EmailService
from services.llm_service import LLMService
from services.search_service import SearchService
from services.slack_service import SlackService
from services.calendar_service import CalendarService
from models import init_db

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(email_bp)
app.register_blueprint(integration_bp)

# Initialize database
init_db()

# Initialize services
email_service = EmailService()
llm_service = LLMService()
search_service = SearchService()
slack_service = SlackService()
calendar_service = CalendarService()

@app.route('/')
def index():
    """Home page route"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('email.inbox'))

@app.route('/dashboard')
def dashboard():
    """Dashboard page showing email overview and assistant capabilities"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('inbox.html')

@app.route('/settings')
def settings():
    """Settings page for configuring the assistant"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('settings.html')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500

# Context processor to make services available in templates
@app.context_processor
def inject_services():
    return {
        'email_service': email_service,
        'llm_service': llm_service,
        'search_service': search_service,
        'slack_service': slack_service,
        'calendar_service': calendar_service
    }

if __name__ == '__main__':
    # Run the app in debug mode for development
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
