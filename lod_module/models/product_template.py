# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_construction_category = fields.Selection([
        ('hormigon', 'Hormigón'),
        ('fierro', 'Fierro/Acero'),
        ('moldaje', 'Moldaje'),
        ('cemento', 'Cemento'),
        ('arena', 'Arena/Gravilla'),
        ('herramientas', 'Herramientas'),
        ('otros', 'Otros'),
    ], string='Categoría Construcción', tracking=True)

    x_warehouse_location = fields.Char('Ubicación en Bodega', tracking=True)
    x_construction_supplier = fields.Char('Proveedor Construcción')
    x_minimum_stock = fields.Float('Stock Mínimo', default=0.0, digits=(16, 2))
    x_construction_notes = fields.Text('Notas de Construcción')

    x_construction_state = fields.Selection([
        ('available', 'Disponible'),
        ('low', 'Stock Bajo'),
        ('out', 'Sin Stock'),
    ], string='Estado Stock', compute='_compute_construction_state')

    @api.depends('qty_available', 'x_minimum_stock')
    def _compute_construction_state(self):
        for rec in self:
            if rec.qty_available <= 0:
                rec.x_construction_state = 'out'
            elif rec.qty_available <= rec.x_minimum_stock:
                rec.x_construction_state = 'low'
            else:
                rec.x_construction_state = 'available'
