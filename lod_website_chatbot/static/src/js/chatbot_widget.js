/** @odoo-module **/

// funcion que se ejecuta al cargar el archivo, sirve para cargar el chatbot. 
(function() {
    'use strict';

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initChatbot);
    } else {
        initChatbot();
    }
   // funcion para cargar el chatbot , se define como una funcion anonima para que no se ejecute 
   // al cargar el archivo solo lo ejecuta cuando se llama
   // html para cargar el chatbot 
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
        // inserta el chatbot en el body usando insertAdjacentHTML
        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
        
        // selecciona los elementos del chatbot , usando getElementById estos elementos estan definidos en el html. 
        const chatbot = document.getElementById('lod-chatbot');
        const toggleBtn = document.getElementById('lod-chatbot-toggle');
        const closeBtn = document.getElementById('lod-chatbot-close');
        const messagesDiv = document.getElementById('lod-chatbot-messages');
        const input = document.getElementById('lod-chatbot-input');
        const sendBtn = document.getElementById('lod-chatbot-send');
        const typingIndicator = document.getElementById('lod-chatbot-typing');
        
        // agrega los eventos a los botones, usando addEventListener
        toggleBtn.addEventListener('click', toggleChat);
        closeBtn.addEventListener('click', toggleChat);
        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
 
        // funciones para el chatbot, su funcion es controlar el chatbot. toggleChat es para abrir y cerrar el chatbot
        function toggleChat() {
            chatbot.classList.toggle('lod-chatbot-closed'); // toggle para cerrar y abrir el chatbot
            chatbot.classList.toggle('lod-chatbot-open'); // toggle para cerrar y abrir el chatbot
            if (chatbot.classList.contains('lod-chatbot-open')) {// si el chatbot esta abierto se enfoca el input
                input.focus();
            }
        }
        // funcion para enviar el mensaje, usando async para que sea asincrona
       // esta funcion asincrona envia el mensaje al chatbot y espera la respuesta. 
       async function sendMessage() {
            const message = input.value.trim(); // quita los espacios en blanco al inicio y al final del mensaje
            if (!message) return; // si el mensaje esta vacio no hace nada

            addMessage(message, 'user'); // agrega el mensaje del usuario
            input.value = ''; // limpia el input

            typingIndicator.style.display = 'flex'; // muestra el indicador de typing
            scrollToBottom(); // scrollea al final del chat
            
            // envia el mensaje al chatbot
            try {
                const response = await fetch('/api/chatbot/ask', { // ruta de la api modulo python  
                    method: 'POST', // metodo post
                    headers: {'Content-Type': 'application/json'}, // tipo de contenido
                    body: JSON.stringify({ // envia el mensaje en formato json
                        jsonrpc: "2.0", // version de jsonrpc
                        method: "call", // metodo de llamada
                        params: {message: message}//parametros del mensaje
                    })
                });
              // recibe la respuesta del chatbot
                const data = await response.json();
                typingIndicator.style.display = 'none'; // oculta el indicador de typing
                // agrega el mensaje del chatbot
                if (data.result && data.result.success) {
                    renderComponent(data.result); // renderiza el componente según el tipo
                } else {
                    const errorMsg = data.result?.error || 'Error al procesar tu consulta';
                    addMessage(errorMsg, 'error');
                }
             // maneja el error
            } catch (error) {
                console.error('Error:', error); // muestra el error en la consola
                typingIndicator.style.display = 'none'; // oculta el indicador de typing
                addMessage('Problema de conexión. Intenta nuevamente.', 'error'); // agrega el mensaje de error
            }
        }
        // agrega el mensaje al chat
        function addMessage(text, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `lod-message lod-message-${type}`; // agrega la clase del mensaje
            messageDiv.innerHTML = `<div class="lod-message-content">${escapeHtml(text)}</div>`; // agrega el contenido del mensaje
            messagesDiv.appendChild(messageDiv); // agrega el mensaje al chat
            scrollToBottom(); // scrollea al final del chat
        }
        // scrollea al final del chat
        function scrollToBottom() {
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        // escapa el html
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // renderiza el componente según el tipo devuelto por el backend
        function renderComponent(payload) {
            const type = payload.type || 'text';
            // Siempre mostrar el texto amigable de Gemini
            if (payload.text) {
                addMessage(payload.text, 'bot');
            }
            // Renderizar componente visual si hay data
            if (payload.data) {
                switch(type) {
                    case 'material_table':
                        renderMaterialTable(payload.data);
                        break;
                    case 'contact_card':
                        renderContactCard(payload.data);
                        break;
                    case 'product_list':
                        renderProductList(payload.data);
                        break;
                }
            }
        }

        // renderiza tabla de materiales con badges de estado
        function renderMaterialTable(materials) {
            if (!materials || materials.length === 0) return;

            let rows = '';
            for (const m of materials) {
                const stateLabel = m.state === 'available' ? 'Disponible'
                    : m.state === 'low' ? 'Stock bajo' : 'Agotado';
                const stateClass = m.state === 'available' ? 'lod-state-available'
                    : m.state === 'low' ? 'lod-state-low' : 'lod-state-out';
                rows += '<tr>'
                    + '<td>' + escapeHtml(m.name) + '</td>'
                    + '<td>' + escapeHtml(String(m.quantity)) + ' ' + escapeHtml(m.unit) + '</td>'
                    + '<td><span class="lod-state-badge ' + stateClass + '">' + escapeHtml(stateLabel) + '</span></td>'
                    + '</tr>';
            }

            const html = '<div class="lod-component-table">'
                + '<table><thead><tr><th>Material</th><th>Cantidad</th><th>Estado</th></tr></thead>'
                + '<tbody>' + rows + '</tbody></table></div>';

            addComponentHTML(html);
        }

        // renderiza card de contacto con links clickeables
        function renderContactCard(data) {
            if (!data) return;

            let content = '<div class="lod-component-card">';
            if (data.name) {
                content += '<div class="lod-card-name">' + escapeHtml(data.name) + '</div>';
            }
            if (data.phone) {
                content += '<div class="lod-card-row"><span class="lod-card-icon">📞</span>'
                    + '<a href="tel:' + escapeHtml(data.phone) + '">' + escapeHtml(data.phone) + '</a></div>';
            }
            if (data.email) {
                content += '<div class="lod-card-row"><span class="lod-card-icon">📧</span>'
                    + '<a href="mailto:' + escapeHtml(data.email) + '">' + escapeHtml(data.email) + '</a></div>';
            }
            content += '</div>';

            addComponentHTML(content);
        }

        // renderiza lista de productos con precios
        function renderProductList(products) {
            if (!products || products.length === 0) return;

            let items = '';
            for (const p of products) {
                const price = p.price > 0
                    ? '$' + Number(p.price).toLocaleString('es-CL')
                    : 'Consultar';
                items += '<div class="lod-product-item">'
                    + '<span class="lod-product-name">' + escapeHtml(p.name) + '</span>'
                    + '<span class="lod-product-price">' + escapeHtml(price) + '</span>'
                    + '</div>';
            }

            const html = '<div class="lod-component-product">' + items + '</div>';
            addComponentHTML(html);
        }

        // inserta HTML de componente como mensaje bot en el chat
        function addComponentHTML(html) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'lod-message lod-message-bot';
            messageDiv.innerHTML = '<div class="lod-message-content lod-component">' + html + '</div>';
            messagesDiv.appendChild(messageDiv);
            scrollToBottom();
        }
    }
})();

// en resumen ese codigo es el chatbot que se muestra en la pagina web , su estructura es la siguiente:
// 1. Crea el chatbot
// 2. Agrega los eventos a los botones
// 3. Agrega las funciones del chatbot
// 4. Agrega el mensaje del usuario
// 5. Agrega el mensaje del chatbot
// 6. Agrega el mensaje del error
// 7. Agrega el mensaje del typing. 