// 1. Message Send karne ka function
function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    
    if (!message) return;

    // User ka message screen par dikhana
    appendMessage(message, 'user-message');
    input.value = ''; // Input khali karna

    // Bot "soch" raha hai (Animation)
    showTyping();

    // Flask Server se baat karna
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(res => res.json())
    .then(data => {
        // Typing animation hatana
        hideTyping();
        
        // Bot ka reply screen par dikhana
        appendMessage(data.reply, 'bot-message');
        
        // Bot ka reply BOL KAR sunana (Text-to-Speech)
        speakText(data.reply);
    })
    .catch(error => {
        console.error('Error:', error);
        hideTyping();
    });
}

// 2. Screen par message bubble banane ka function
function appendMessage(text, className) {
    const chatBox = document.getElementById('chat-box');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${className}`;
    msgDiv.innerText = text;
    chatBox.appendChild(msgDiv);
    
    // Auto-scroll neeche tak
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 3. Typing Animation (. . .) dikhana
function showTyping() {
    const chatBox = document.getElementById('chat-box');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'message bot-message';
    typingDiv.innerHTML = '<span>.</span><span>.</span><span>.</span>';
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function hideTyping() {
    const loader = document.getElementById('typing-indicator');
    if (loader) loader.remove();
}

// 4. Voice Recognition (Mic se Text)
function startDictation() {
    if (window.hasOwnProperty('webkitSpeechRecognition')) {
        var recognition = new webkitSpeechRecognition();
        recognition.lang = "en-US";
        recognition.start();

        const micBtn = document.getElementById('mic-btn');
        micBtn.style.boxShadow = "0 0 20px #ff007f"; // Recording glow

        recognition.onresult = function(e) {
            const transcript = e.results[0][0].transcript;
            document.getElementById('user-input').value = transcript;
            recognition.stop();
            micBtn.style.boxShadow = "0 0 10px var(--primary-neon)";
            
            // Awaz milte hi message send kar dena
            sendMessage();
        };

        recognition.onerror = function() {
            recognition.stop();
            micBtn.style.boxShadow = "0 0 10px var(--primary-neon)";
        };
    } else {
        alert("Mic not supported in this browser.");
    }
}

// 5. Text-to-Speech (Bot ka bolna)
function speakText(text) {
    if ('speechSynthesis' in window) {
        // Purani awaz ko stop karna
        window.speechSynthesis.cancel();

        const msg = new SpeechSynthesisUtterance(text);
        msg.lang = 'en-US';
        msg.rate = 1;  // Speed
        msg.pitch = 1; // Tone
        
        window.speechSynthesis.speak(msg);
    }
}

// Enter key se message bhejna
document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});
