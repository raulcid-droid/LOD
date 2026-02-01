# -*- coding: utf-8 -*-
from odoo import models
import logging
import re

_logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
except ImportError:
    genai = None
    _logger.warning("google-generativeai no instalada")

class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    def _message_post_after_hook(self, message, msg_vals):
        res = super()._message_post_after_hook(message, msg_vals)
        
        # 1. ESCUDO ANTI-BUCLE: No responder a sistemas, bots o notificaciones
        if not message.author_id or \
           message.author_id.id == self.env.ref('base.partner_root').id or \
           message.message_type == 'notification':
            return res

        # Solo actuar en el canal del Asistente
        if self.name != 'Asistente de Construcción':
            return res
        
        body = message.body or ''
        
        # 2. ESCUDO ANTI-BUCLE: Si el mensaje contiene nuestros propios emojis de respuesta, ignorar
        if "📦" in body or "✅" in body or "❌" in body:
            return res

        clean_text = re.sub('<[^>]*>', '', body).strip()
        
        if clean_text and len(clean_text) > 0:
            try:
                # Obtener API Key de los ajustes
                api_key = self.env['ir.config_parameter'].sudo().get_param('construction_materials.api_key')
                
                if not api_key:
                    _logger.warning("API Key de Gemini no configurada en Ajustes")
                    return res
                
                if not genai:
                    _logger.error("Librería google-generativeai no disponible")
                    return res
                
                # Consultar Inventario de lod_module
                materials = self.env['construction.material'].search([])
                inventory_text = "📦 **INVENTARIO ACTUAL:**\n\n"
                for mat in materials:
                    # Determinar emoji según el estado definido en tu lod_module
                    emoji = "✅" if mat.state == 'available' else "⚠️" if mat.state == 'low' else "❌"
                    inventory_text += f"{emoji} **{mat.name}**: {mat.quantity} {mat.unit}\n"
                
                # Configurar y llamar a Gemini
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                prompt = f"""Eres un experto en construcción chileno para el Libro de Obras Digital.

{inventory_text}

DATOS TÉCNICOS DE REFERENCIA:
- Hormigón H30: 10-12 m³ para 100m²
- Fierro A630-420H: 800-1000 kg para 100m²
- Moldaje: 100-120 m² para 100m²

Usuario pregunta: {clean_text}

Responde de forma técnica y breve si el stock actual es suficiente para lo que el usuario consulta."""

                response = model.generate_content(prompt)
                
                if response and response.text:
                    # Publicar respuesta (el escudo del paso 2 evitará que esto dispare un bucle)
                    self.message_post(body=response.text, message_type='comment')
                    
            except Exception as e:
                # Registramos el error en el log de Odoo.sh pero NO lo enviamos al chat
                _logger.error(f"FALLO CRÍTICO EN ASISTENTE IA: {str(e)}")
        
        return res
