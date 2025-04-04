document.addEventListener("DOMContentLoaded", function() {
    const chatBox = document.querySelector(".chat-box");
    const userInput = document.querySelector("#user-input");
    const sendBtn = document.querySelector("#send-btn");

    function appendMessage(sender, message) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("chat-message");
        msgDiv.classList.add(sender);
        msgDiv.innerHTML = message;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    sendBtn.addEventListener("click", function() {
        const userMessage = userInput.value.trim();
        if (userMessage) {
            appendMessage("user", `<strong>You:</strong> ${userMessage}`);
            userInput.value = "";
            fetchResponse(userMessage);
        }
    });

    function fetchResponse(userMessage) {
        setTimeout(() => {
            let botResponse = "I am processing your request...";
            if (userMessage.toLowerCase().includes("shoes")) {
                botResponse = `Sure! We have about 4 shoe brands under $200:
                <ul>
                    <li>Air Rike: <a href='#'>fashionstore/airrike</a></li>
                    <li>Versace Covers: <a href='#'>fashionstore/versace</a></li>
                    <li>Rope Sandals: <a href='#'>fashionstore/rope</a></li>
                    <li>Sweaty Crocs: <a href='#'>fashionstore/sweaty</a></li>
                </ul>`;
            } else {
                botResponse = "Sorry, I couldn't understand your request.";
            }
            appendMessage("bot", `<strong>Bot:</strong> ${botResponse}`);
        }, 1000);
    }
});
msgDiv.innerHTML
