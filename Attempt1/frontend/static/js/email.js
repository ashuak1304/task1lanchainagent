// Email handling functionality

function initializeEmailList() {
    // Set up email list click handlers
    const emailList = document.querySelector('.email-list');
    if (emailList) {
        emailList.addEventListener('click', function(e) {
            const emailItem = e.target.closest('.email-item');
            if (emailItem) {
                const emailId = emailItem.dataset.emailId;
                viewEmail(emailId);
            }
        });
    }
    
    // Set up email action buttons
    document.querySelectorAll('.email-action-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const action = this.dataset.action;
            const emailId = this.closest('.email-view').dataset.emailId;
            
            handleEmailAction(action, emailId);
        });
    });
}

function loadEmails() {
    showLoader();
    
    fetch('/api/emails')
        .then(response => response.json())
        .then(data => {
            renderEmailList(data.emails);
            hideLoader();
        })
        .catch(error => {
            console.error('Error loading emails:', error);
            showError('Failed to load emails. Please try again later.');
            hideLoader();
        });
}

function renderEmailList(emails) {
    const emailListContainer = document.querySelector('.email-list');
    if (!emailListContainer) return;
    
    emailListContainer.innerHTML = '';
    
    if (emails.length === 0) {
        emailListContainer.innerHTML = '<div class="no-emails">No emails found</div>';
        return;
    }
    
    emails.forEach(email => {
        const emailItem = document.createElement('div');
        emailItem.className = `email-item ${email.is_read ? '' : 'unread'}`;
        emailItem.dataset.emailId = email.id;
        
        emailItem.innerHTML = `
            <div class="email-sender">${escapeHtml(email.sender_name || email.sender)}</div>
            <div class="email-subject">${escapeHtml(email.subject)}</div>
            <div class="email-date">${formatDate(email.received_at)}</div>
        `;
        
        emailListContainer.appendChild(emailItem);
    });
}

function viewEmail(emailId) {
    showLoader();
    
    fetch(`/api/email/${emailId}`)
        .then(response => response.json())
        .then(email => {
            renderEmailView(email);
            
            // Mark as read if not already
            if (!email.is_read) {
                markAsRead(emailId);
            }
            
            hideLoader();
        })
        .catch(error => {
            console.error('Error loading email:', error);
            showError('Failed to load email. Please try again later.');
            hideLoader();
        });
}

function renderEmailView(email) {
    const emailViewContainer = document.querySelector('.email-view');
    if (!emailViewContainer) return;
    
    emailViewContainer.dataset.emailId = email.id;
    
    emailViewContainer.innerHTML = `
        <div class="email-header">
            <h2 class="email-subject-header">${escapeHtml(email.subject)}</h2>
            <div class="email-metadata">
                <div>
                    <strong>From:</strong> ${escapeHtml(email.sender_name || email.sender)} &lt;${escapeHtml(email.sender)}&gt;<br>
                    <strong>To:</strong> ${escapeHtml(email.recipient)}<br>
                    ${email.cc ? `<strong>CC:</strong> ${escapeHtml(email.cc)}<br>` : ''}
                    <strong>Date:</strong> ${formatDate(email.received_at, true)}
                </div>
                <div class="email-actions">
                    <button class="btn btn-primary email-action-btn" data-action="reply">Reply</button>
                    <button class="btn btn-outline email-action-btn" data-action="forward">Forward</button>
                    <button class="btn btn-outline email-action-btn" data-action="ai-reply">AI Reply</button>
                </div>
            </div>
        </div>
        <div class="email-content">
            ${email.body_html || `<pre>${escapeHtml(email.body_text)}</pre>`}
        </div>
        ${email.attachments && email.attachments.length > 0 ? renderAttachments(email.attachments) : ''}
    `;
    
    // Show email view
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });
    document.getElementById('email-view-section').style.display = 'block';
    
    // Set up action buttons
    initializeEmailList();
}

function renderAttachments(attachments) {
    let html = '<div class="email-attachments"><h3>Attachments</h3><ul>';
    
    attachments.forEach(attachment => {
        html += `
            <li class="attachment-item">
                <a href="/api/attachment/${attachment.id}" target="_blank">
                    ${getAttachmentIcon(attachment.content_type)}
                    ${escapeHtml(attachment.filename)}
                    (${formatFileSize(attachment.size)})
                </a>
            </li>
        `;
    });
    
    html += '</ul></div>';
    return html;
}

function handleEmailAction(action, emailId) {
    switch (action) {
        case 'reply':
            composeReply(emailId);
            break;
        case 'forward':
            forwardEmail(emailId);
            break;
        case 'ai-reply':
            generateAIReply(emailId);
            break;
        case 'archive':
            archiveEmail(emailId);
            break;
        default:
            console.error('Unknown email action:', action);
    }
}

function markAsRead(emailId) {
    fetch(`/api/email/${emailId}/read`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        // Update UI to reflect read status
        const emailItem = document.querySelector(`.email-item[data-email-id="${emailId}"]`);
        if (emailItem) {
            emailItem.classList.remove('unread');
        }
    })
    .catch(error => {
        console.error('Error marking email as read:', error);
    });
}
