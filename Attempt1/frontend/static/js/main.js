// Main JavaScript file for AI Personal Email Assistant

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeNavigation();
    initializeEmailList();
    initializeCompose();
    initializeAIFeatures();
    
    // Check authentication status
    checkAuthStatus();
});

// Handle navigation and routing
function initializeNavigation() {
    const navLinks = document.querySelectorAll('nav a, .sidebar-menu-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                navigateTo(targetId);
            }
        });
    });
    
    // Handle browser back/forward buttons
    window.addEventListener('popstate', function(e) {
        if (e.state && e.state.page) {
            loadContent(e.state.page);
        }
    });
    
    // Initial page load based on URL hash
    const initialPage = window.location.hash.substring(1) || 'inbox';
    navigateTo(initialPage, false);
}

function navigateTo(pageId, addToHistory = true) {
    loadContent(pageId);
    
    // Update active navigation link
    document.querySelectorAll('nav a, .sidebar-menu-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + pageId) {
            link.classList.add('active');
        }
    });
    
    // Add to browser history
    if (addToHistory) {
        window.history.pushState({ page: pageId }, '', '#' + pageId);
    }
}

function loadContent(pageId) {
    // Hide all content sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Show the requested section
    const targetSection = document.getElementById(pageId + '-section');
    if (targetSection) {
        targetSection.style.display = 'block';
    }
    
    // Load data for specific pages
    if (pageId === 'inbox') {
        loadEmails();
    } else if (pageId === 'settings') {
        loadSettings();
    }
}

// Check if user is authenticated
function checkAuthStatus() {
    fetch('/auth/status')
        .then(response => response.json())
        .then(data => {
            if (!data.authenticated) {
                window.location.href = '/auth/login';
            }
        })
        .catch(error => {
            console.error('Error checking authentication status:', error);
        });
}
