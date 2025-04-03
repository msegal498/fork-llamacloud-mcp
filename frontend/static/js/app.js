// Get DOM elements
const chatbox = document.getElementById('chatbox');
const input = document.getElementById('input');

// Initialize chat
document.addEventListener('DOMContentLoaded', () => {
    addWelcomeMessage();
});

// Add welcome message
function addWelcomeMessage() {
    const welcomeMsg = document.createElement('div');
    welcomeMsg.className = 'message agent-message';
    welcomeMsg.innerHTML = '<strong>LlamaCloud Agent:</strong> Welcome! Ask me a question about LlamaIndex documentation.';
    chatbox.appendChild(welcomeMsg);
}

// Send message function
function sendMessage() {
    const query = input.value.trim();
    if (!query) return;
    
    // Add user message to chat
    addUserMessage(query);
    
    // Show loading indicator
    const loadingId = addLoadingIndicator();
    
    // Send to server
    fetch('/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading indicator
        removeLoadingIndicator(loadingId);
        
        // Display response
        if (data.response) {
            addAgentMessage(data.response);
        } else if (data.error) {
            addErrorMessage(data.error);
        } else {
            addErrorMessage('No response received');
        }
    })
    .catch(error => {
        // Remove loading indicator
        removeLoadingIndicator(loadingId);
        
        // Display error
        addErrorMessage(error.message);
    });
    
    // Clear input
    input.value = '';
}

// Add user message to chat
function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `<strong>You:</strong> ${escapeHtml(text)}`;
    chatbox.appendChild(messageDiv);
    scrollToBottom();
}

// Add agent message to chat
function addAgentMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent-message';
    messageDiv.innerHTML = `<strong>LlamaCloud Agent:</strong> ${escapeHtml(text)}`;
    chatbox.appendChild(messageDiv);
    scrollToBottom();
}

// Add error message to chat
function addErrorMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message error-message';
    messageDiv.innerHTML = `<strong>Error:</strong> ${escapeHtml(text)}`;
    chatbox.appendChild(messageDiv);
    scrollToBottom();
}

// Add loading indicator
function addLoadingIndicator() {
    const id = 'loading-' + Date.now();
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message loading';
    loadingDiv.id = id;
    loadingDiv.textContent = 'Processing';
    chatbox.appendChild(loadingDiv);
    scrollToBottom();
    return id;
}

// Remove loading indicator
function removeLoadingIndicator(id) {
    const loadingIndicator = document.getElementById(id);
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

// Scroll chat to bottom
function scrollToBottom() {
    chatbox.scrollTop = chatbox.scrollHeight;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add event listener for Enter key
input.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});
