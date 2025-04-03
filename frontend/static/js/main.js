/**
 * PDF Chunking System Frontend Script
 * Handles PDF upload, status checking, and download interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const uploadForm = document.getElementById('pdf-upload-form');
    const uploadSection = document.getElementById('upload-section');
    const statusSection = document.getElementById('status-section');
    const resultSection = document.getElementById('result-section');
    const errorSection = document.getElementById('error-section');
    
    const statusIndicator = document.getElementById('status-indicator');
    const statusMessage = document.getElementById('status-message');
    const progressBar = document.getElementById('progress-bar');
    
    const resultDetails = document.getElementById('result-details');
    const downloadLink = document.getElementById('download-link');
    const newUploadBtn = document.getElementById('new-upload-btn');
    const retryBtn = document.getElementById('retry-btn');
    
    let currentJobId = null;
    let statusCheckInterval = null;
    
    // Handle form submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const fileInput = document.getElementById('pdf-file');
        const file = fileInput.files[0];
        
        if (!file) {
            showError('Please select a PDF file to upload.');
            return;
        }
        
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showError('Please select a valid PDF file.');
            return;
        }
        
        try {
            // Show status section
            uploadSection.classList.add('hidden');
            statusSection.classList.remove('hidden');
            resultSection.classList.add('hidden');
            errorSection.classList.add('hidden');
            
            // Set initial status
            updateStatus('pending', 'Uploading PDF file...');
            progressBar.style.width = '10%';
            
            // Upload file
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/pdf/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }
            
            const data = await response.json();
            currentJobId = data.job_id;
            
            // Start checking status
            updateStatus('processing', 'Processing PDF...');
            progressBar.style.width = '40%';
            
            // Start status polling
            startStatusPolling(currentJobId);
            
        } catch (error) {
            console.error('Upload error:', error);
            showError('Failed to upload PDF: ' + error.message);
        }
    });
    
    // Function to start polling for status updates
    function startStatusPolling(jobId) {
        // Clear any existing interval
        if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
        }
        
        // Poll every 2 seconds
        statusCheckInterval = setInterval(async () => {
            try {
                const response = await fetch(`/pdf/status/${jobId}`);
                
                if (!response.ok) {
                    throw new Error(`Status check failed: ${response.statusText}`);
                }
                
                const data = await response.json();
                const status = data.status;
                
                if (status === 'uploaded' || status === 'processing') {
                    // Still processing
                    updateStatus('processing', `Processing PDF... (${status})`);
                    progressBar.style.width = status === 'uploaded' ? '50%' : '70%';
                } else if (status === 'complete') {
                    // Processing complete
                    clearInterval(statusCheckInterval);
                    progressBar.style.width = '100%';
                    showResults(data);
                } else if (status === 'error') {
                    // Error occurred
                    clearInterval(statusCheckInterval);
                    showError(data.error || 'An unknown error occurred during processing.');
                }
                
            } catch (error) {
                console.error('Status check error:', error);
                clearInterval(statusCheckInterval);
                showError('Failed to check processing status: ' + error.message);
            }
        }, 2000);
    }
    
    // Function to update status display
    function updateStatus(statusType, message) {
        statusIndicator.className = 'status ' + statusType;
        statusIndicator.textContent = statusType.charAt(0).toUpperCase() + statusType.slice(1);
        statusMessage.textContent = message;
    }
    
    // Function to show results
    function showResults(data) {
        // Hide status section and show results
        statusSection.classList.add('hidden');
        resultSection.classList.remove('hidden');
        
        // Format and display result details
        const result = data.result || {};
        let detailsHTML = `
            <div class="result-item">
                <strong>Original File:</strong> ${data.original_filename || 'Unknown'}
            </div>
            <div class="result-item">
                <strong>Text Extracted:</strong> ${formatNumber(result.extracted_text_length || 0)} characters
            </div>
            <div class="result-item">
                <strong>Chunks Created:</strong> ${result.num_chunks || 0}
            </div>
            <div class="result-item">
                <strong>Summary Length:</strong> ${formatNumber(result.summary_length || 0)} characters
            </div>
        `;
        
        resultDetails.innerHTML = detailsHTML;
        
        // Set download link
        downloadLink.href = `/pdf/download/${currentJobId}`;
        downloadLink.setAttribute('download', `processed_${data.original_filename || 'document'}`);
    }
    
    // Function to show error message
    function showError(message) {
        // Hide other sections
        uploadSection.classList.add('hidden');
        statusSection.classList.add('hidden');
        resultSection.classList.add('hidden');
        errorSection.classList.remove('hidden');
        
        // Display error
        document.getElementById('error-message').textContent = message;
    }
    
    // Function to format numbers with commas
    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }
    
    // New upload button click handler
    newUploadBtn.addEventListener('click', () => {
        resetForm();
    });
    
    // Retry button click handler
    retryBtn.addEventListener('click', () => {
        resetForm();
    });
    
    // Function to reset form and UI
    function resetForm() {
        // Clear the file input
        uploadForm.reset();
        
        // Clear any polling interval
        if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
            statusCheckInterval = null;
        }
        
        // Reset progress bar
        progressBar.style.width = '0%';
        
        // Show upload section, hide others
        uploadSection.classList.remove('hidden');
        statusSection.classList.add('hidden');
        resultSection.classList.add('hidden');
        errorSection.classList.add('hidden');
        
        // Clear job ID
        currentJobId = null;
    }
});
