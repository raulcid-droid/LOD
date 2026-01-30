def _message_post_after_hook(self, message, msg_vals):
        res = super()._message_post_after_hook(message, msg_vals)
        
        # LOG DE SEGURIDAD: Esto DEBE aparecer en tu terminal al escribir
        _logger.info(">>> ASISTENTE LOD: Procesando mensaje en canal %s", self.name)

        # 1. FILTRO FLEXIBLE: Si el nombre tiene 'asistente' (sin importar tildes o mayúsculas)
        if 'asistente' not in self.name.lower():
            return res
        
        # 2. EVITAR BUCLE: No responder a la propia IA
        if message.author_id.id == self.env.ref('base.partner_root').id:
            return res
        
        body = message.body or ''
        clean_text = re.sub('<[^>]*>', '', body).strip()
        
        if clean_text:
            try:
                api_key = self.env['ir.config_parameter'].sudo().get_param('lod_module.construction_api_key')
                if not api_key:
                    _logger.warning(">>> ASISTENTE LOD: Falta API Key en Ajustes")
                    return res
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Obtenemos materiales
                materials = self.env['construction.material'].sudo().search([])
                inventory_text = "Inventario:\n" + "\n".join([f"- {m.name}: {m.quantity} {m.unit}" for m in materials])
                
                response = model.generate_content(f"Contexto: {inventory_text}\nPregunta: {clean_text}")
                
                if response and response.text:
                    self.sudo().message_post(
                        body=response.text, 
                        author_id=self.env.ref('base.partner_root').id,
                        message_type='comment'
                    )
            except Exception as e:
                _logger.error(">>> ASISTENTE LOD ERROR: %s", str(e))
        
        return res
