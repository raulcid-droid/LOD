# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    construction_api_key = fields.Char(
        string='Gemini API Key',
        config_parameter='construction_materials.api_key',
        help='API Key de Google Gemini para el asistente IA'
    )
