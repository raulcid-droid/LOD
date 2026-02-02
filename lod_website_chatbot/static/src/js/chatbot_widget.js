/** @odoo-module **/

(function() {
    'use strict';

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initChatbot);
    } else {
        initChatbot();
    }

    function initChatbot() {
        const chatbotHTML = `
            <div id="lod-chatbot" class="lod-chatbot-closed">
                <button id="lod-chatbot-toggle" class="lod-chatbot-toggle">
                    <span class="lod-chatbot-icon">💬</span>
                    <span class="lod-chatbot-text">Consultas</span>
                </button>

                <div id="lod-chatbot-window" class="lod-chatbot-window">
                    <div class="lod-chatbot-header">
                        <div class="lod-chatbot-title">
                            <span class="lod-chatbot-avatar">🏗️</span>
                            <div>
                                <h3>Asistente de Construcción</h3>
                                <p class="lod-chatbot-status">En línea</p>
                            </div>
                        </div>
                        <button id="lod-chatbot-close" class="lod-chatbot-close">✕</button>
                    </div>

                    <div id="lod-chatbot-messages" class="lod-chatbot-messages">
                        <div class="lod-message lod-message-bot">
                            <div class="lod-message-content">
                                ¡Hola! 👋 Soy tu asistente virtual. Puedo ayudarte con consultas sobre materiales de construcción. ¿En qué puedo ayudarte?
                            </div>
                        </div>
                    </div>

                    <div class="lod-chatbot-input-container">
                        <input type="text" id="lod-chatbot-input" class="lod-chatbot-input" placeholder="Escribe tu pregunta..." autocomplete="off"/>
                        <button id="lod-chatbot-send" class="lod-chatbot-send">Enviar</button>
                    </div>

                    <div id="lod-chatbot-typing" class="lod-chatbot-typing" style="display: none;">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', chatbotHTML);

        const chatbot = document.getElementById('lod-chatbot');
        const toggleBtn = document.getElementById('lod-chatbot-toggle');
        const closeBtn = document.getElementById('lod-chatbot-close');
        const messagesDiv = document.getElementById('lod-chatbot-messages');
        const input = document.getElementById('lod-chatbot-input');
        const sendBtn = document.getElementById('lod-chatbot-send');
        const typingIndicator = document.getElementById('lod-chatbot-typing');

        toggleBtn.addEventListener('click', toggleChat);
        closeBtn.addEventListener('click', toggleChat);
        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        function toggleChat() {
            chatbot.classList.toggle('lod-chatbot-closed');
            chatbot.classList.toggle('lod-chatbot-open');
            if (chatbot.classList.contains('lod-chatbot-open')) {
                input.focus();
            }
        }

        async function sendMessage() {
            const message = input.value.trim();
            if (!message) return;

            addMessage(message, 'user');
            input.value = '';

            typingIndicator.style.display = 'flex';
            scrollToBottom();

            try {
                const response = await fetch('/api/chatbot/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        jsonrpc: "2.0",
                        method: "call",
                        params: {message: message}
                    })
                });

                const data = await response.json();
                typingIndicator.style.display = 'none';

                if (data.result && data.result.success) {
                    addMessage(data.result.response, 'bot');
                } else {
                    const errorMsg = data.result?.error || 'Error al procesar tu consulta';
                    addMessage(errorMsg, 'error');
                }

            } catch (error) {
                console.error('Error:', error);
                typingIndicator.style.display = 'none';
                addMessage('Problema de conexión. Intenta nuevamente.', 'error');
            }
        }

        function addMessage(text, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `lod-message lod-message-${type}`;
            messageDiv.innerHTML = `<div class="lod-message-content">${escapeHtml(text)}</div>`;
            messagesDiv.appendChild(messageDiv);
            scrollToBottom();
        }

        function scrollToBottom() {
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    }
})();
