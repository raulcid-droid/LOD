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
                    case 'product_detail':
                        renderProductDetail(payload.data);
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

        // genera un placeholder SVG según la categoría del producto
        function getCategoryPlaceholder(category) {
            var cat = (category || '').toLowerCase();
            var icon, color;
            if (cat.indexOf('hormig') !== -1 || cat.indexOf('concret') !== -1) {
                icon = 'M4 20h16v-2H4v2zm0-4h16v-2H4v2zm0-4h16v-2H4v2zm0-4h16V6H4v2zm0-4h16V2H4v2z';
                color = '7c8a96';
            } else if (cat.indexOf('fierro') !== -1 || cat.indexOf('acero') !== -1 || cat.indexOf('metal') !== -1) {
                icon = 'M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14l-5-5 1.41-1.41L12 14.17l6.59-6.59L20 9l-8 8z';
                color = '6b7b8d';
            } else if (cat.indexOf('moldaje') !== -1 || cat.indexOf('encofr') !== -1) {
                icon = 'M3 3h18v2H3V3zm0 16h18v2H3v-2zm0-8h18v2H3v-2zm4-4h10v2H7V7zm0 8h10v2H7v-2z';
                color = '8d6e63';
            } else if (cat.indexOf('cement') !== -1) {
                icon = 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z';
                color = '9e9e9e';
            } else if (cat.indexOf('arena') !== -1) {
                icon = 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z';
                color = 'c8a951';
            } else if (cat.indexOf('herramienta') !== -1 || cat.indexOf('tool') !== -1) {
                icon = 'M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z';
                color = 'f4a236';
            } else {
                icon = 'M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V6h16v12zM6 10h2v2H6v-2zm0 4h8v2H6v-2zm10 0h2v2h-2v-2zm-6-4h8v2h-8v-2z';
                color = '667eea';
            }
            return 'data:image/svg+xml,' + encodeURIComponent(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
                + '<rect width="64" height="64" rx="8" fill="#' + color + '22"/>'
                + '<svg x="16" y="16" width="32" height="32" viewBox="0 0 24 24">'
                + '<path fill="#' + color + '" d="' + icon + '"/>'
                + '</svg></svg>'
            );
        }

        // renderiza lista de productos con precios y thumbnails
        function renderProductList(products) {
            if (!products || products.length === 0) return;

            let items = '';
            for (const p of products) {
                const price = p.price > 0
                    ? '$' + Number(p.price).toLocaleString('es-CL')
                    : 'Consultar';
                const imgSrc = p.image_url
                    ? escapeHtml(p.image_url)
                    : getCategoryPlaceholder(p.category);
                items += '<div class="lod-product-item">'
                    + '<img class="lod-product-thumb" src="' + imgSrc
                    + '" alt="" onerror="this.src=\'' + getCategoryPlaceholder(p.category) + '\'" />'
                    + '<span class="lod-product-name">' + escapeHtml(p.name) + '</span>'
                    + '<span class="lod-product-price">' + escapeHtml(price) + '</span>'
                    + '</div>';
            }

            const html = '<div class="lod-component-product">' + items + '</div>';
            addComponentHTML(html);
        }

        // renderiza card de detalle de un producto específico
        function renderProductDetail(data) {
            if (!data) return;

            let content = '<div class="lod-component-detail">';
            var imgSrc = data.image_url
                ? escapeHtml(data.image_url)
                : getCategoryPlaceholder(data.category);
            content += '<img class="lod-detail-image" src="' + imgSrc
                + '" alt="' + escapeHtml(data.name || '') + '"'
                + ' onerror="this.src=\'' + getCategoryPlaceholder(data.category) + '\'" />';
            if (data.name) {
                content += '<div class="lod-detail-name">' + escapeHtml(data.name) + '</div>';
            }
            if (data.category) {
                content += '<div class="lod-detail-category">' + escapeHtml(data.category) + '</div>';
            }
            if (data.description) {
                content += '<div class="lod-detail-desc">' + escapeHtml(data.description) + '</div>';
            }
            if (data.price > 0) {
                content += '<div class="lod-detail-price">$'
                    + Number(data.price).toLocaleString('es-CL') + '</div>';
            }
            content += '</div>';

            addComponentHTML(content);
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