def _message_post_after_hook(self, message, msg_vals):
        res = super()._message_post_after_hook(message, msg_vals)
        
        # 1. FILTRO DE CANAL: Solo actuar en el asistente
        if self.name != 'Asistente de Construcción':
            return res
        
        # 2. EL FRENO (IMPORTANTE): Si el autor es el sistema (OdooBot) o la IA, NO RESPONDER
        # Esto evita que la respuesta de la IA gatille una nueva respuesta
        if message.author_id.id == self.env.ref('base.partner_root').id or message.author_id.name == 'OdooBot':
            return res
        
        body = message.body or ''
        clean_text = re.sub('<[^>]*>', '', body).strip()
        
        if clean_text and len(clean_text) > 0:
            try:
                # OJO: Cambiamos el parámetro al que configuramos en el XML anteriormente
                api_key = self.env['ir.config_parameter'].sudo().get_param('lod_module.construction_api_key')
                
                if not api_key:
                    # Usamos sudo() para postear sin disparar restricciones
                    self.sudo().message_post(body="⚠️ **API Key no configurada**\n\nVe a: Settings → Construction Materials AI")
                    return res
                
                if not genai:
                    self.sudo().message_post(body="⚠️ Librería google-generativeai no instalada")
                    return res
                
                materials = self.env['construction.material'].sudo().search([])
                
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
                    # Publicamos la respuesta usando sudo para asegurar el posteo
                    self.sudo().message_post(body=response.text, author_id=self.env.ref('base.partner_root').id)
                else:
                    self.sudo().message_post(body="❌ No pude generar respuesta")
                    
            except Exception as e:
                _logger.error(f"Error IA: {str(e)}")
                # Evitamos postear el error si es un tema de recursión para no alimentar el bucle
                if "recursion" not in str(e).lower():
                    self.sudo().message_post(body=f"❌ Error técnico en IA")
        
        return res
