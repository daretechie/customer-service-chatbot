document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const fileInput = document.getElementById('fileInput');
    const uploadSubmit = document.getElementById('uploadSubmit');
    const faqBtn = document.getElementById('faqBtn');
    const faqModal = document.getElementById('faqModal');
    const closeModal = document.querySelector('.close');
    const faqContent = document.getElementById('faqContent');
    
    let currentDocumentHash = '';
    
    // Send message function
    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addMessage(message, 'user');
        userInput.value = '';
        
        // Get bot response
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: message,
                document_hash: currentDocumentHash
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                addMessage(data.error, 'bot');
                return;
            }
            addMessage(data.response, 'bot');
            
            // For debugging: show which chunks were used
            if (data.relevant_chunks) {
                console.log("Used these document chunks:", data.relevant_chunks);
            }
        })
        .catch(error => {
            addMessage("Sorry, I'm having trouble connecting to the server.", 'bot');
            console.error('Error:', error);
        });
    }
    
    // Add message to chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        messageDiv.innerHTML = `<p>${text}</p>`;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Upload document
    uploadSubmit.addEventListener('click', function() {
        if (fileInput.files.length === 0) {
            alert('Please select a file first');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        addMessage("Processing your document...", 'bot');
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                addMessage(data.error, 'bot');
                return;
            }
            
            currentDocumentHash = data.document_hash;
            
            // Update UI
            document.getElementById('businessType').textContent = `Document Support (${data.chunk_count} chunks)`;
            
            addMessage("Document processed successfully! I'm ready to answer your questions.", 'bot');
            addMessage(`I've generated ${data.faqs.split('Q:').length - 1} FAQs based on your document.`, 'bot');
            
            // Store FAQs
            faqContent.innerHTML = data.faqs.replace(/\n/g, '<br>');
        })
        .catch(error => {
            addMessage("Failed to process document. Please try again.", 'bot');
            console.error('Error:', error);
        });
    });
    
    // FAQ modal
    faqBtn.addEventListener('click', function() {
        if (!currentDocumentHash) {
            addMessage("Please upload a document first to generate FAQs.", 'bot');
            return;
        }
        faqModal.style.display = 'block';
    });
    
    closeModal.addEventListener('click', function() {
        faqModal.style.display = 'none';
    });
    
    window.addEventListener('click', function(event) {
        if (event.target === faqModal) {
            faqModal.style.display = 'none';
        }
    });
    
    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });
});
