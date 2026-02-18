# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ConstructionMaterial(models.Model):
    _name = 'construction.material'
    _description = 'Material de Construcción'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char('Material', required=True, tracking=True)
    code = fields.Char('Código', tracking=True)
    image = fields.Image('Imagen', max_width=256, max_height=256)
    
    category = fields.Selection([
        ('hormigon', 'Hormigón'),
        ('fierro', 'Fierro/Acero'),
        ('moldaje', 'Moldaje'),
        ('cemento', 'Cemento'),
        ('arena', 'Arena/Gravilla'),
        ('herramientas', 'Herramientas'),
        ('otros', 'Otros')
    ], string='Categoría', required=True, default='otros', tracking=True)
    
    unit = fields.Selection([
        ('m3', 'Metro Cúbico (m³)'),
        ('kg', 'Kilogramo (kg)'),
        ('ton', 'Tonelada (ton)'),
        ('unidad', 'Unidad'),
        ('ml', 'Metro Lineal (ml)'),
        ('m2', 'Metro Cuadrado (m²)'),
        ('saco', 'Saco'),
    ], string='Unidad', required=True, default='unidad', tracking=True)
    
    quantity = fields.Float('Cantidad Disponible', default=0.0, tracking=True, digits=(16, 2))
    minimum_stock = fields.Float('Stock Mínimo', default=0.0, digits=(16, 2))
    location = fields.Char('Ubicación en Bodega', tracking=True)
    supplier = fields.Char('Proveedor')
    notes = fields.Text('Notas')
    
    state = fields.Selection([
        ('available', 'Disponible'),
        ('low', 'Stock Bajo'),
        ('out', 'Sin Stock')
    ], string='Estado', compute='_compute_state', store=True)
    
    @api.depends('quantity', 'minimum_stock')
    def _compute_state(self):
        for record in self:
            if record.quantity <= 0:
                record.state = 'out'
            elif record.quantity <= record.minimum_stock:
                record.state = 'low'
            else:
                record.state = 'available'
