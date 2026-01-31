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
        
        if self.name != 'Asistente de Construcción':
            return res
        
        if message.author_id.id == self.env.ref('base.partner_root').id:
            return res
        
        body = message.body or ''
        clean_text = re.sub('<[^>]*>', '', body).strip()
        
        if clean_text and len(clean_text) > 0:
            try:
                api_key = self.env['ir.config_parameter'].sudo().get_param('construction_materials.api_key')
                
                if not api_key:
                    self.message_post(body="⚠️ **API Key no configurada**\n\nVe a: Settings → Construction Materials AI")
                    return res
                
                if not genai:
                    self.message_post(body="⚠️ Librería google-generativeai no instalada")
                    return res
                
                materials = self.env['construction.material'].search([])
                
                inventory_text = "📦 **INVENTARIO ACTUAL:**\n\n"
                for mat in materials:
                    emoji = "✅" if mat.state == 'available' else "⚠️" if mat.state == 'low' else "❌"
                    inventory_text += f"{emoji} **{mat.name}**: {mat.quantity} {mat.unit}\n"
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                prompt = f"""Eres un experto en construcción chileno.

{inventory_text}

CANTIDADES TÍPICAS PARA LOSA 100m²:
- Hormigón H30: 10-12 m³
- Fierro A630-420H: 800-1000 kg  
- Moldaje: 100-120 m²

Pregunta: {clean_text}

Responde profesionalmente si hay suficiente stock."""

                response = model.generate_content(prompt)
                
                if response and response.text:
                    self.message_post(body=response.text)
                else:
                    self.message_post(body="❌ No pude generar respuesta")
                    
            except Exception as e:
                _logger.error(f"Error IA: {str(e)}")
                self.message_post(body=f"❌ Error: {str(e)}")
        
        return res
