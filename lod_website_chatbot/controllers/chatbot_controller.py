# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)

class ChatbotWebController(http.Controller):
    
    @http.route('/api/chatbot/ask', type='json', auth='public', methods=['POST'], csrf=False, cors='*') # Define la ruta de la API
    def chatbot_ask(self, message, **kwargs): # Define la función que se ejecutará cuando se acceda a la ruta
        """API pública para consultas del chatbot web con acceso a contenido del sitio""" # Descripción de la función
        try:
            if not message or len(message.strip()) < 3:
                return {'success': False, 'error': 'Por favor escribe una pregunta más específica'}
            
            # Obtener API Key
            api_key = request.env['ir.config_parameter'].sudo().get_param('construction_materials.api_key')
            
            if not api_key:
                _logger.error("API Key de Gemini no configurada")
                return {'success': False, 'error': 'Chatbot no disponible'}
            
            # Verificar librería
            try:
                import google.generativeai as genai
            except ImportError:
                _logger.error("Librería google-generativeai no instalada")
                return {'success': False, 'error': 'Servicio no disponible'}
            
            # ==============================================================================================
            # 1. RETRIEVAL (RECUPERACIÓN)
            # ==============================================================================================
            # En esta etapa, el sistema busca datos relevantes en "tiempo real" desde la base de datos de Odoo.
            # Estos datos recuperados formarán el "contexto" que se enviará al modelo.
            
            # Consultar inventario
            materials = request.env['construction.material'].sudo().search([]) # Busca todos los materiales
            
            if not materials:
                inventory_text = "📦 No hay materiales en inventario.\n"
            else:
                inventory_text = "📦 MATERIALES DISPONIBLES:\n\n"
                for mat in materials:
                    emoji = "✅" if mat.state == 'available' else "⚠️" if mat.state == 'low' else "❌"
                    inventory_text += f"{emoji} {mat.name}: {mat.quantity} {mat.unit}\n"
            
            # Consultar contenido del website
            website_content = ""
            
            # Páginas del website
            try:
                pages = request.env['website.page'].sudo().search([('website_published', '=', True)], limit=10, order='name')
                if pages:
                    website_content += "\n📄 PÁGINAS DEL SITIO:\n"
                    for page in pages:
                        website_content += f"- {page.name} ({page.url})\n"
            except:
                pass
            
            # Productos publicados
            try:
                products = request.env['product.template'].sudo().search([('website_published', '=', True)], limit=10, order='name')
                if products:
                    website_content += "\n🛒 PRODUCTOS/SERVICIOS:\n"
                    for prod in products:
                        price = f"${prod.list_price:,.0f}" if hasattr(prod, 'list_price') and prod.list_price > 0 else "Consultar"
                        website_content += f"- {prod.name}: {price}\n"
            except:
                pass
            
            # Posts del blog
            try:
                posts = request.env['blog.post'].sudo().search([('website_published', '=', True)], limit=5, order='create_date desc')
                if posts:
                    website_content += "\n📝 ÚLTIMOS ARTÍCULOS:\n"
                    for post in posts:
                        website_content += f"- {post.name}\n"
            except:
                pass
            
            # Información de contacto
            try:
                company = request.env['res.company'].sudo().browse(1)
                if company:
                    website_content += "\n🏢 CONTACTO:\n"
                    if company.phone:
                        website_content += f"- Teléfono: {company.phone}\n"
                    if company.email:
                        website_content += f"- Email: {company.email}\n"
            except:
                pass
            
            # Configurar Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-flash-latest')
            
            # ==============================================================================================
            # 2. AUGMENTATION (AUMENTACIÓN)
            # ==============================================================================================
            # Aquí "aumentamos" el conocimiento del modelo inyectando los datos recuperados directamente en el prompt.
            # El modelo (Gemini) no conoce tu inventario ni tus páginas web, pero aquí se lo "enseñamos" 
            # dinámicamente en cada consulta dentro de las variables {inventory_text} y {website_content}.
            # f string es una cadena de texto que permite incluir variables dentro de la cadena

            prompt = f"""Eres el asistente virtual de LOD - Libro de Obras Digital.

{inventory_text}

{website_content}

DATOS TÉCNICOS:
- Hormigón H30: 10-12 m³ por 100m²
- Fierro A630-420H: 800-1000 kg por 100m²
- Moldaje: 100-120 m² por 100m²

Pregunta del usuario: {message.strip()}

INSTRUCCIONES DE RESPUESTA:
Responde SIEMPRE en formato JSON válido con esta estructura:
{{
  "type": "text|material_table|contact_card|product_list",
  "text": "tu mensaje amigable y breve (máximo 3 líneas)"
}}

Reglas para elegir el type:
- "material_table": cuando pregunten por materiales, inventario, stock, disponibilidad
- "contact_card": cuando pregunten por contacto, teléfono, email, dirección
- "product_list": cuando pregunten por productos, servicios, precios, catálogo
- "text": para todo lo demás (saludos, dudas técnicas, cálculos, etc.)

IMPORTANTE: Responde SOLO el JSON, sin markdown, sin backticks, sin texto adicional."""
            
            # ==============================================================================================
            # 3. GENERATION (GENERACIÓN)
            # ==============================================================================================
            # Finalmente, enviamos el prompt enriquecido al LLM. El modelo procesa la pregunta del usuario
            # JUNTOS con los datos del inventario y contenido web que le acabamos de pasar, y "genera" 
            # una respuesta en lenguaje natural basada en esa información exacta.

            response = model.generate_content(prompt)

            if not response or not response.text:
                raise Exception("Sin respuesta")

            _logger.info(f"Chatbot respondió: '{message[:50]}'")

            # Parsear JSON de Gemini
            raw_text = response.text.strip()
            try:
                ai_response = json.loads(raw_text)
                component_type = ai_response.get('type', 'text')
                friendly_text = ai_response.get('text', raw_text)
            except (json.JSONDecodeError, AttributeError):
                # Fallback: si Gemini no devuelve JSON válido, tratar como texto
                component_type = 'text'
                friendly_text = raw_text

            # Construir respuesta con datos reales de Odoo según el tipo
            result = {
                'success': True,
                'type': component_type,
                'text': friendly_text,
            }

            if component_type == 'material_table':
                result['data'] = [{
                    'name': m.name,
                    'quantity': m.quantity,
                    'unit': m.unit,
                    'state': m.state,
                    'category': m.category,
                } for m in materials]

            elif component_type == 'contact_card':
                company = request.env['res.company'].sudo().browse(1)
                result['data'] = {
                    'phone': company.phone or '',
                    'email': company.email or '',
                    'name': company.name or '',
                }

            elif component_type == 'product_list':
                products = request.env['product.template'].sudo().search(
                    [('website_published', '=', True)], limit=10, order='name')
                result['data'] = [{
                    'name': p.name,
                    'price': p.list_price,
                } for p in products]

            return result
            
        except Exception as e:
            _logger.error(f"Error chatbot: {str(e)}")
            if 'Quota exceeded' in str(e):
                return {'success': False, 'error': 'Servicio saturado. Intenta en unos minutos.'}
            return {'success': False, 'error': 'Error del servidor.'}
