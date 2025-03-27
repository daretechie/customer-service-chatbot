document.addEventListener('DOMContentLoaded', () => {
    const sendButton = document.getElementById('send-button');
    const userInput = document.getElementById('user-input');
    const chatHistory = document.getElementById('chat-history');

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        userInput.value = '';
        addMessage('user', message);
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message})
            });
            
            if (!response.ok) throw new Error('API error');
            const data = await response.json();
            addMessage('bot', data.response);
        } catch (error) {
            addMessage('error', 'Could not get response');
        }
    }

    function addMessage(type, content) {
        const div = document.createElement('div');
        div.className = `${type}-message`;
        div.textContent = content;
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});