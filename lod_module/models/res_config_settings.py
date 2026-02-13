# -*- coding: utf-8 -*-
from odoo import fields, models. # odoo es el framework que usamos


class ResConfigSettings(models.TransientModel): # heredamos de res.config.settings
    _inherit = 'res.config.settings' # heredamos de res.config.settings

    construction_api_key = fields.Char( # campos de configuracion
        string='Gemini API Key', # string es el nombre que se muestra en el formulario
        config_parameter='construction_materials.api_key', # config_parameter es el nombre que le damos a la variable
        help='API Key de Google Gemini para el asistente IA' # help es la ayuda que se muestra en el formulario
    )
