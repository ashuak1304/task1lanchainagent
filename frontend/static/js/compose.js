// Email composition functionality

function initializeCompose() {
    const composeForm = document.getElementById('compose-form');
    if (composeForm) {
        composeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendEmail();
        });
    }
    
    // New email button
    const newEmailBtn = document.getElementById('new-email-btn');
    if (newEmailBtn) {
        newEmailBtn.addEventListener('click', function() {
            showComposeForm();
        });
    }
}

function showComposeForm(replyTo = null, forward = null) {
    // Show compose section
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });
    document.getElementById('compose-section').style.display = 'block';
    
    const composeForm = document.getElementById('compose-form');
    
    // Clear form
    composeForm.reset();
    
    // Set form title and action
    const formTitle = document.querySelector('#compose-section h2');
    
    if (replyTo) {
        formTitle.textContent = 'Reply to Email';
        composeForm.dataset.action = 'reply';
        composeForm.dataset.emailId = replyTo.id;
        
        // Pre-fill fields
        document.getElementById('compose-to').value = replyTo.sender;
        document.getElementById('compose-subject').value = `Re: ${replyTo.subject.replace(/^Re: /, '')}`;
        
        // Set cursor to message body
        setTimeout(() => {
            document.getElementById('compose-body').focus();
        }, 100);
    } else if (forward) {
        formTitle.textContent = 'Forward Email';
        composeForm.dataset.action = 'forward';
        composeForm.dataset.emailId = forward.id;
        
        // Pre-fill fields
        document.getElementById('compose-subject').value = `Fwd: ${forward.subject.replace(/^Fwd: /, '')}`;
        document.getElementById('compose-body').value = `\n\n---------- Forwarded message ----------\nFrom: ${forward.sender}\nDate: ${formatDate(forward.received_at, true)}\nSubject: ${forward.subject}\nTo: ${forward.recipient}\n\n${forward.body_text}`;
        
        // Set cursor to recipient field
        setTimeout(() => {
            document.getElementById('compose-to').focus();
        }, 100);
    } else {
        formTitle.textContent = 'New Email';
        composeForm.dataset.action = 'new';
        delete composeForm.dataset.emailId;
        
        // Set cursor to recipient field
        setTimeout(() => {
            document.getElementById('compose-to').focus();
        }, 100);
    }
}

function composeReply(emailId) {
    showLoader();
    
    fetch(`/api/email/${emailId}`)
        .then(response => response.json())
        .then(email => {
            showComposeForm(email);
            hideLoader();
        })
        .catch(error => {
            console.error('Error loading email for reply:', error);
            showError('Failed to load email for reply. Please try again later.');
            hideLoader();
        });
}

function forwardEmail(emailId) {
    showLoader();
    
    fetch(`/api/email/${emailId}`)
        .then(response => response.json())
        .then(email => {
            showComposeForm(null, email);
            hideLoader();
        })
        .catch(error => {
            console.error('Error loading email for forwarding:', error);
            showError('Failed to load email for forwarding. Please try again later.');
            hideLoader();
        });
}

function sendEmail() {
    const composeForm = document.getElementById('compose-form');
    const action = composeForm.dataset.action || 'new';
    const emailId = composeForm.dataset.emailId;
    
    const to = document.getElementById('compose-to').value;
    const cc = document.getElementById('compose-cc').value;
    const subject = document.getElementById('compose-subject').value;
    const body = document.getElementById('compose-body').value;
    
    if (!to) {
        showError('Please specify at least one recipient.');
        return;
    }
    
    if (!subject) {
        if (!confirm('Send this email without a subject?')) {
            return;
        }
    }
    
    showLoader();
    
    let endpoint = '/api/email/send';
    let method = 'POST';
    
    if (action === 'reply') {
        endpoint = `/api/email/${emailId}/reply`;
    }
    
    fetch(endpoint, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            to: to,
            cc: cc,
            subject: subject,
            body: body
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Email sent successfully!');
            navigateTo('inbox');
        } else {
            showError(data.message || 'Failed to send email. Please try again later.');
        }
        hideLoader();
    })
    .catch(error => {
        console.error('Error sending email:', error);
        showError('Failed to send email. Please try again later.');
        hideLoader();
    });
}
