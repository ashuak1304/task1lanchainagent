// AI functionality for the email assistant

function initializeAIFeatures() {
    // AI reply button
    document.addEventListener('click', function(e) {
        if (e.target.matches('.email-action-btn[data-action="ai-reply"]')) {
            const emailId = e.target.closest('.email-view').dataset.emailId;
            generateAIReply(emailId);
        }
    });
    
    // Calendar detection
    document.addEventListener('click', function(e) {
        if (e.target.matches('.create-event-btn')) {
            const eventData = JSON.parse(e.target.dataset.event);
            createCalendarEvent(eventData);
        }
    });
    
    // Web search integration
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = document.getElementById('search-query').value;
            performWebSearch(query);
        });
    }
    
    // Slack integration
    document.addEventListener('click', function(e) {
        if (e.target.matches('.send-to-slack-btn')) {
            const emailId = e.target.dataset.emailId;
            sendToSlack(emailId);
        }
    });
}

function generateAIReply(emailId) {
    showLoader();
    
    fetch(`/api/generate/reply/${emailId}`)
        .then(response => response.json())
        .then(data => {
            // Load the compose form with AI-generated reply
            fetch(`/api/email/${emailId}`)
                .then(response => response.json())
                .then(email => {
                    showComposeForm(email);
                    
                    // Insert AI-generated reply
                    document.getElementById('compose-body').value = data.reply_text;
                    
                    hideLoader();
                    
                    // Show AI confidence indicator
                    showSuccess(`AI generated a reply with ${Math.round(data.confidence * 100)}% confidence`);
                })
                .catch(error => {
                    console.error('Error loading email for AI reply:', error);
                    hideLoader();
                });
        })
        .catch(error => {
            console.error('Error generating AI reply:', error);
            showError('Failed to generate AI reply. Please try again later.');
            hideLoader();
        });
}

function performWebSearch(query) {
    showLoader();
    
    fetch('/api/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: query,
            num_results: 5
        })
    })
    .then(response => response.json())
    .then(data => {
        renderSearchResults(data.results);
        hideLoader();
    })
    .catch(error => {
        console.error('Error performing web search:', error);
        showError('Failed to perform web search. Please try again later.');
        hideLoader();
    });
}

function renderSearchResults(results) {
    const resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = '';
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="no-results">No results found</div>';
        return;
    }
    
    const resultsList = document.createElement('div');
    resultsList.className = 'search-results-list';
    
    results.forEach(result => {
        const resultItem = document.createElement('div');
        resultItem.className = 'search-result-item';
        
        resultItem.innerHTML = `
            <h3><a href="${result.link}" target="_blank">${escapeHtml(result.title)}</a></h3>
            <div class="search-result-url">${escapeHtml(result.link)}</div>
            <div class="search-result-snippet">${escapeHtml(result.snippet)}</div>
        `;
        
        resultsList.appendChild(resultItem);
    });
    
    resultsContainer.appendChild(resultsList);
    
    // Show the search results section
    document.getElementById('search-results-section').style.display = 'block';
}

function createCalendarEvent(eventData) {
    showLoader();
    
    fetch('/api/calendar/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            event: eventData
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Calendar event created successfully!');
            if (data.event_id && data.html_link) {
                showCalendarEventDetails(data.event_id, data.html_link);
            }
        } else {
            showError(data.message || 'Failed to create calendar event. Please try again later.');
        }
        hideLoader();
    })
    .catch(error => {
        console.error('Error creating calendar event:', error);
        showError('Failed to create calendar event. Please try again later.');
        hideLoader();
    });
}

function showCalendarEventDetails(eventId, htmlLink) {
    const detailsContainer = document.createElement('div');
    detailsContainer.className = 'calendar-event-details';
    detailsContainer.innerHTML = `
        <p>Event created successfully! <a href="${htmlLink}" target="_blank">View in Calendar</a></p>
    `;
    
    const resultsSection = document.getElementById('calendar-results-section');
    if (resultsSection) {
        resultsSection.innerHTML = '';
        resultsSection.appendChild(detailsContainer);
        resultsSection.style.display = 'block';
    }
}

function sendToSlack(emailId) {
    showLoader();
    
    fetch(`/api/email/${emailId}`)
        .then(response => response.json())
        .then(email => {
            // Get email summary from LLM
            return fetch('/api/analyze/email/' + emailId)
                .then(response => response.json())
                .then(analysis => {
                    // Send to Slack
                    return fetch('/api/slack/send', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            channel: document.getElementById('slack-channel')?.value || 'general',
                            message: `*Email from ${email.sender_name || email.sender}*\n*Subject:* ${email.subject}\n\n${analysis.summary}`
                        })
                    });
                });
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccess('Email sent to Slack successfully!');
            } else {
                showError(data.message || 'Failed to send to Slack. Please try again later.');
            }
            hideLoader();
        })
        .catch(error => {
            console.error('Error sending to Slack:', error);
            showError('Failed to send to Slack. Please try again later.');
            hideLoader();
        });
}

// Utility functions for AI features
function detectEventInEmail(emailBody) {
    showLoader();
    
    fetch('/api/analyze/event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: emailBody
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.event) {
            showEventDetectionUI(data.event);
        }
        hideLoader();
    })
    .catch(error => {
        console.error('Error detecting event:', error);
        hideLoader();
    });
}

function showEventDetectionUI(eventData) {
    const container = document.createElement('div');
    container.className = 'detected-event-container';
    
    container.innerHTML = `
        <div class="detected-event">
            <h3>Event Detected</h3>
            <p><strong>Summary:</strong> ${escapeHtml(eventData.summary)}</p>
            <p><strong>Date:</strong> ${formatDate(eventData.start.dateTime)}</p>
            <p><strong>Time:</strong> ${formatTime(eventData.start.dateTime)} - ${formatTime(eventData.end.dateTime)}</p>
            ${eventData.location ? `<p><strong>Location:</strong> ${escapeHtml(eventData.location)}</p>` : ''}
            <button class="btn btn-primary create-event-btn" data-event='${JSON.stringify(eventData)}'>Add to Calendar</button>
        </div>
    `;
    
    const emailView = document.querySelector('.email-view');
    if (emailView) {
        emailView.appendChild(container);
    }
}

// Helper function to format dates for display
function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Helper functions for UI feedback
function showLoader() {
    const loader = document.getElementById('loader');
    if (loader) loader.style.display = 'block';
}

function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) loader.style.display = 'none';
}

function showSuccess(message) {
    const notification = document.createElement('div');
    notification.className = 'notification success';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

function showError(message) {
    const notification = document.createElement('div');
    notification.className = 'notification error';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}
