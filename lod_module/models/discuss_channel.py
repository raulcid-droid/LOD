# -*- coding: utf-8 -*-
from odoo import models
import logging
import re 

_logger = logging.getLogger(__name__) # logger para debugging

try:
    import google.generativeai as genai # Importamos la librería de Google Gemini
except ImportError:
    genai = None
    _logger.warning("google-generativeai no instalada")

class DiscussChannel(models.Model):
    _inherit = 'discuss.channel' # heredamos de discuss.channel

    def _message_post_after_hook(self, message, msg_vals):
        """
        Hook que se ejecuta después de publicar un mensaje en el canal.
        Responde automáticamente con IA solo a mensajes de usuarios reales.
        """
        res = super()._message_post_after_hook(message, msg_vals)
        
        # ==========================================
        # ESCUDOS ANTI-BUCLE - ORDEN CRÍTICO
        # ==========================================
        
        # ESCUDO 1: Verificar que el contexto no tenga la marca de "bot procesando"
        # Esto previene que el hook se dispare cuando el bot publica su respuesta
        if self.env.context.get('skip_bot_response'):
            return res
        
        # ESCUDO 2: No responder a notificaciones del sistema
        if message.message_type == 'notification':
            return res
        
        # ESCUDO 3: No responder si no hay autor (mensajes automáticos)
        if not message.author_id:
            return res
        
        # ESCUDO 4: No responder a mensajes del partner root (sistema)
        try:
            root_partner = self.env.ref('base.partner_root')
            if message.author_id.id == root_partner.id:
                return res
        except:
            pass  # Si no existe base.partner_root, continuar
        
        # ESCUDO 5: Solo actuar en el canal correcto
        if self.name != 'Asistente de Construcción':
            return res
        
        # ==========================================
        # PROCESAMIENTO DEL MENSAJE
        # ==========================================
        
        body = message.body or ''
        
        # Limpiar HTML del mensaje
        clean_text = re.sub('<[^>]*>', '', body).strip()
        
        # Solo procesar si hay texto válido (más de 2 caracteres)
        if not clean_text or len(clean_text) < 3:
            return res
        
        # Log para debugging
        _logger.info(f"BOT procesando mensaje: '{clean_text[:50]}...'")
        
        try:
            # ==========================================
            # CONFIGURACIÓN DE LA IA
            # ==========================================
            
            # Obtener API Key desde configuración de Odoo
            api_key = self.env['ir.config_parameter'].sudo().get_param('construction_materials.api_key')
            
            if not api_key:
                _logger.warning("API Key de Gemini no configurada en Ajustes")
                return res
            
            if not genai:
                _logger.error("Librería google-generativeai no disponible")
                return res
            
            # ==========================================
            # CONSULTAR INVENTARIO
            # ==========================================
            
            materials = self.env['construction.material'].search([])
            
            if not materials:
                inventory_text = "📦 **INVENTARIO VACÍO** - No hay materiales registrados.\n"
            else:
                inventory_text = "📦 **INVENTARIO ACTUAL:**\n\n"
                for mat in materials:
                    # Determinar emoji según estado
                    if mat.state == 'available':
                        emoji = "✅"
                    elif mat.state == 'low':
                        emoji = "⚠️"
                    else:
                        emoji = "❌"
                    
                    inventory_text += f"{emoji} **{mat.name}**: {mat.quantity} {mat.unit}\n"
            
            # ==========================================
            # LLAMAR A GEMINI
            # ==========================================
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-flash-latest')
            
            prompt = f"""Eres un asistente técnico experto en construcción para el Libro de Obras Digital de Chile.

{inventory_text}

DATOS TÉCNICOS DE REFERENCIA:
- Hormigón H30: 10-12 m³ por cada 100m²
- Fierro A630-420H: 800-1000 kg por cada 100m²
- Moldaje: 100-120 m² por cada 100m²

PREGUNTA DEL USUARIO: {clean_text}

INSTRUCCIONES:
- Responde de forma técnica, precisa y concisa (máximo 2-3 líneas)
- Si preguntan por cantidad, indica el stock disponible
- Si preguntan por suficiencia, compara con los datos técnicos de referencia
- Si no hay datos suficientes para responder, indícalo claramente
- Usa lenguaje profesional pero amigable"""

            response = model.generate_content(prompt)
            
            if response and response.text:
                # ==========================================
                # PUBLICAR RESPUESTA CON CONTEXTO ESPECIAL
                # ==========================================
                
                # Crear un nuevo contexto con la marca para evitar bucles
                new_context = dict(self.env.context, skip_bot_response=True)
                
                # Publicar con el contexto modificado
                self.with_context(new_context).message_post(
                    body=response.text,
                    message_type='comment'
                )
                
                _logger.info(f"BOT respondió exitosamente")
                
        except Exception as e:
            # Log del error sin mostrar al usuario
            _logger.error(f"ERROR EN ASISTENTE IA: {str(e)}")
        
        return res
