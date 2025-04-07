import streamlit as st
import pandas as pd
from datetime import datetime
import os
import uuid
import json

# Import modules
from modules.email_integration import GmailIntegration
from modules.llm_processor import LLMProcessor
from modules.slack_integration import SlackIntegration
from modules.search_integration import SearchIntegration
from modules.calendar_integration import CalendarIntegration
from modules.memory_manager import get_email_by_id, get_all_emails, save_response
from utils.helpers import truncate_text, format_datetime

# Initialize session state variables if they don't exist
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.selected_email = None
    st.session_state.draft_response = ""
    st.session_state.search_results = ""
    st.session_state.meeting_details = {}
    st.session_state.available_slots = []

# Initialize components
@st.cache_resource
def load_llm():
    return LLMProcessor()

@st.cache_resource
def load_gmail():
    return GmailIntegration()

@st.cache_resource
def load_slack():
    return SlackIntegration()

@st.cache_resource
def load_search():
    return SearchIntegration()

@st.cache_resource
def load_calendar():
    return CalendarIntegration()

# Load components
llm = load_llm()
gmail = load_gmail()
slack = load_slack()
search = load_search()
calendar = load_calendar()

# App title and description
st.title("AI Personal Email Assistant")
st.markdown("A tool to help manage your emails with AI assistance")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Inbox", "Compose", "Settings", "About"])

# Inbox page
if page == "Inbox":
    st.header("Email Inbox")
    
    # Refresh button for emails
    if st.button("Refresh Inbox"):
        with st.spinner("Fetching emails..."):
            gmail.get_emails(max_results=20)
        st.success("Inbox refreshed!")
    
    # Get emails from database
    emails = get_all_emails(limit=50)
    
    if not emails:
        st.info("No emails found. Click 'Refresh Inbox' to fetch emails.")
    else:
        # Create a DataFrame for display
        email_data = []
        for email in emails:
            email_data.append({
                "ID": email.id,
                "From": email.sender,
                "Subject": truncate_text(email.subject, 40),
                "Date": format_datetime(email.timestamp, "%b %d, %Y %H:%M") if email.timestamp else "Unknown",
                "Has Attachment": "Yes" if email.has_attachment else "No"
            })
        
        df = pd.DataFrame(email_data)
        
        # Display emails in a table
        st.dataframe(df, use_container_width=True)
        
        # Email selection
        selected_id = st.selectbox("Select an email to view:", 
                                  options=[email.id for email in emails],
                                  format_func=lambda x: next((e["Subject"] for e in email_data if e["ID"] == x), x))
        
        if selected_id:
            st.session_state.selected_email = get_email_by_id(selected_id)
            
            if st.session_state.selected_email:
                email = st.session_state.selected_email
                
                # Display email details
                st.subheader("Email Details")
                st.markdown(f"**From:** {email.sender}")
                st.markdown(f"**To:** {email.recipient}")
                st.markdown(f"**Subject:** {email.subject}")
                st.markdown(f"**Date:** {format_datetime(email.timestamp) if email.timestamp else 'Unknown'}")
                
                # Email body
                st.markdown("### Email Content")
                st.text_area("Body", email.body, height=200, disabled=True)
                
                # Email analysis
                with st.expander("Email Analysis"):
                    if st.button("Analyze Email"):
                        with st.spinner("Analyzing email..."):
                            # Classify email
                            classification = llm.classify_email(email.body)
                            st.markdown(f"**Classification:**\n{classification}")
                            
                            # Summarize email
                            summary = llm.summarize_email(email.body)
                            st.markdown(f"**Summary:**\n{summary}")
                            
                            # Check if it's a meeting request
                            if "Meeting Request" in classification:
                                meeting_details = llm.extract_meeting_details(email.body)
                                st.session_state.meeting_details = meeting_details
                                
                                st.markdown("**Meeting Details:**")
                                for key, value in meeting_details.items():
                                    st.markdown(f"- **{key}:** {value}")
                                
                                # Get available slots
                                if "Date" in meeting_details:
                                    st.markdown("**Available Time Slots:**")
                                    available_slots = calendar.suggest_meeting_times(
                                        meeting_details.get("Date", ""),
                                        int(meeting_details.get("Duration", "60"))
                                    )
                                    st.session_state.available_slots = available_slots
                                    
                                    for slot in available_slots:
                                        st.markdown(f"- {slot}")
                
                # Generate response
                st.markdown("### Response Options")
                
                if st.button("Generate Response"):
                    with st.spinner("Generating response..."):
                        # Generate search query if needed
                        search_query = llm.generate_search_query(email.body)
                        
                        # Get search results
                        search_results = search.search_and_format(search_query, num_results=3)
                        st.session_state.search_results = search_results
                        
                        # Generate response with search context
                        response = llm.generate_response(
                            email.body, 
                            email.sender, 
                            context=search_results
                        )
                        
                        st.session_state.draft_response = response
                
                # Display draft response
                if st.session_state.draft_response:
                    st.text_area("Draft Response", st.session_state.draft_response, height=200)
                    
                    # Edit response
                    edited_response = st.text_area("Edit Response (if needed)", 
                                                 st.session_state.draft_response, 
                                                 height=200)
                    
                    # Send options
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("Send Response"):
                            with st.spinner("Sending email..."):
                                # Save response to database
                                response_data = {
                                    "id": str(uuid.uuid4()),
                                    "email_id": email.id,
                                    "content": edited_response,
                                    "timestamp": datetime.now(),
                                    "sent": True
                                }
                                save_response(response_data)
                                
                                # Send email
                                sent = gmail.send_email(
                                    to=email.sender,
                                    subject=f"Re: {email.subject}",
                                    body=edited_response,
                                    reply_to_message_id=email.id
                                )
                                
                                if sent:
                                    st.success("Email sent successfully!")
                                else:
                                    st.error("Failed to send email.")
                    
                    with col2:
                        if st.button("Send to Slack"):
                            with st.spinner("Sending to Slack..."):
                                sent = slack.send_response_preview(email.id, edited_response)
                                
                                if sent:
                                    st.success("Response sent to Slack for review!")
                                else:
                                    st.error("Failed to send to Slack.")
                    
                    with col3:
                        if st.button("Schedule Meeting") and st.session_state.meeting_details:
                            with st.spinner("Scheduling meeting..."):
                                event_id = calendar.create_event(st.session_state.meeting_details)
                                
                                if event_id:
                                    st.success("Meeting scheduled successfully!")
                                    
                                    # Send confirmation
                                    confirmation = f"""
                                    I've scheduled a meeting as requested:
                                    
                                    Title: {st.session_state.meeting_details.get('Title', 'Meeting')}
                                    Date: {st.session_state.meeting_details.get('Date', 'Not specified')}
                                    Time: {st.session_state.meeting_details.get('Time', 'Not specified')}
                                    
                                    Looking forward to our discussion.
                                    """
                                    
                                    gmail.send_email(
                                        to=email.sender,
                                        subject=f"Meeting Confirmation: {st.session_state.meeting_details.get('Title', 'Meeting')}",
                                        body=confirmation,
                                        reply_to_message_id=email.id
                                    )
                                else:
                                    st.error("Failed to schedule meeting.")
                
                # Display search results
                if st.session_state.search_results:
                    with st.expander("Search Results"):
                        st.markdown(st.session_state.search_results)

# Compose page
elif page == "Compose":
    st.header("Compose New Email")
    
    recipient = st.text_input("To:")
    subject = st.text_input("Subject:")
    body = st.text_area("Message:", height=200)
    
    if st.button("Send Email"):
        if recipient and subject and body:
            with st.spinner("Sending email..."):
                sent = gmail.send_email(
                    to=recipient,
                    subject=subject,
                    body=body
                )
                
                if sent:
                    st.success("Email sent successfully!")
                else:
                    st.error("Failed to send email.")
        else:
            st.warning("Please fill in all fields.")

# Settings page
elif page == "Settings":
    st.header("Settings")
    
    st.subheader("LLM Settings")
    model_id = st.text_input("Model ID:", "microsoft/Phi-3-mini-4k-instruct")
    temperature = st.slider("Temperature:", 0.0, 1.0, 0.7)
    max_tokens = st.slider("Max Tokens:", 100, 1000, 512)
    
    st.subheader("Email Settings")
    email_limit = st.slider("Number of emails to fetch:", 5, 50, 20)
    
    if st.button("Save Settings"):
        # In a real app, you would save these to a config file or database
        st.success("Settings saved!")

# About page
elif page == "About":
    st.header("About")
    
    st.markdown("""
    ## AI Personal Email Assistant
    
    This application helps you manage your emails using AI assistance. It can:
    
    - Fetch and display emails from your Gmail account
    - Analyze email content and intent
    - Generate appropriate responses
    - Schedule meetings based on email content
    - Search the web for relevant information
    - Send notifications to Slack
    
    ### Technologies Used
    
    - Python
    - Streamlit
    - Transformers (Hugging Face)
    - LangChain
    - SQLite
    - Gmail API
    - Slack API
    - Google Calendar API
    - Google Custom Search API
    
    ### Version
    
    1.0.0
    """)

# Footer
st.markdown("---")
st.markdown("AI Personal Email Assistant | Developed with ❤️ using Python and Transformers")
