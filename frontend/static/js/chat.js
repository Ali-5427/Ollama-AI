document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');

    const API_BASE_URL =
        window.location.hostname === "127.0.0.1" ||
            window.location.hostname === "localhost"
            ? "http://127.0.0.1:5000"
            : "https://chatbot1-xzuk.onrender.com";


    const history = [];

    // Theme + clear buttons (if you added them)
    const themeToggle = document.getElementById('theme-toggle');
    const clearChat = document.getElementById('clear-chat');

    if (themeToggle) {
        if (localStorage.getItem("theme") === "dark") {
            document.body.className = "dark";
            themeToggle.textContent = "☀️";
        }

        themeToggle.addEventListener('click', () => {
            const isDark = document.body.classList.toggle("dark");

            if (isDark) {
                document.body.className = "dark";
                themeToggle.textContent = "☀️";
                localStorage.setItem("theme", "dark");
            } else {
                document.body.className = "light";
                themeToggle.textContent = "🌙";
                localStorage.setItem("theme", "light");
            }
        });
    }

    if (clearChat) {
        clearChat.addEventListener("click", () => {
            chatMessages.innerHTML = "";
            history.length = 0;
            addMessage("Chat cleared. How can I help you now?", "bot");
        });
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const message = userInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        history.push({ role: 'user', text: message });
        userInput.value = '';

        const typingIndicatorId = showTypingIndicator();

        try {
            const response = await fetch(`${API_BASE_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    history: history
                }),
            });

            let data = {};
            try {
                data = await response.json();
            } catch {
                data = {};
            }

            removeTypingIndicator(typingIndicatorId);

            if (!response.ok) {
                const errMsg = data.error || 'Server error';
                addMessage('Error: ' + errMsg, 'bot');
                return;
            }

            const reply = data.reply || 'Sorry, I have no reply.';
            addMessage(reply, 'bot');
            history.push({ role: 'assistant', text: reply });

        } catch (error) {
            removeTypingIndicator(typingIndicatorId);
            addMessage('Sorry, network error. Please try again.', 'bot');
            console.error('Fetch error:', error);
        }
    });

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.textContent = text;

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const indicatorDiv = document.createElement('div');
        indicatorDiv.classList.add('typing-indicator', 'bot-message');
        indicatorDiv.id = id;

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.innerHTML = `
            <span>Typing</span>
            <span class="dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </span>
        `;

        indicatorDiv.appendChild(contentDiv);
        chatMessages.appendChild(indicatorDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    function removeTypingIndicator(id) {
        const indicator = document.getElementById(id);
        if (indicator) {
            indicator.remove();
        }
    }
});
