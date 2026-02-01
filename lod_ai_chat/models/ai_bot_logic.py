from odoo import models, api, fields
import google.generativeai as genai
import logging

_logger = logging.getLogger(__name__)

# --- PEGA TU API KEY AQUI ---
API_KEY = "AIzaSyCemTftdDansp1SZSCvOkSYLve7Ff1q_9c"

class Channel(models.Model):
    _inherit = 'discuss.channel'

    def _get_inventario_resumen(self):
        # Busca productos con stock > 0
        products = self.env['product.product'].search([
            ('type', '=', 'product'),
            ('qty_available', '>', 0)
        ], limit=20)

        txt = "STOCK ACTUAL BODEGA:\n"
        for p in products:
            txt += f"- {p.name}: {p.qty_available} {p.uom_id.name}\n"
        return txt

    def message_post(self, **kwargs):
        message = super(Channel, self).message_post(**kwargs)

        # Evitar bucles y respuestas a notificaciones
        if kwargs.get('author_id') and kwargs.get('message_type') != 'notification':
            user_msg = kwargs.get('body', '')

            # Chequeo simple para que no se responda a sí mismo
            if "OdooBot" not in self.env.user.name and len(user_msg) > 5:
                try:
                    genai.configure(api_key=API_KEY)
                    model = genai.GenerativeModel('gemini-1.5-flash')

                    stock_info = self._get_inventario_resumen()

                    prompt = f"""
                    Eres experto en construcción y asistente de obra.
                    DATOS DE STOCK REAL:
                    {stock_info}

                    INSTRUCCIONES:
                    - Calcula materiales con 10% pérdida.
                    - Revisa si el stock alcanza.
                    - Responde corto y técnico.

                    Usuario: {user_msg}
                    """

                    response = model.generate_content(prompt)

                    # Responder como OdooBot
                    bot = self.env.ref('base.partner_root')
                    self.with_user(self.env.ref('base.user_root')).message_post(
                        body=response.text,
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment',
                        author_id=bot.id
                    )
                except Exception as e:
                    _logger.error(f"Error IA: {e}")

        return message
