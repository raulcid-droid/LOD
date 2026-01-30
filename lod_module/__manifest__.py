# -*- coding: utf-8 -*-
{
    'name': 'Construction Materials AI',
    'version': '19.0.1.0.0',
    'category': 'Construction',
    'summary': 'Gestión de bodega de materiales con asistente IA',
    'description': """
        Módulo para gestión de materiales de construcción con:
        - Control de inventario de materiales
        - Asistente IA para consultas
        - Alertas de stock bajo
    """,
    'author': 'Raul Cid',
    'website': 'https://cidev.dev',
    'depends': ['base', 'mail', 'stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'data/discuss_channel_data.xml',
        'data/demo_materials.xml',
        'views/construction_material_views.xml',
        'views/res_config_settings_views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
