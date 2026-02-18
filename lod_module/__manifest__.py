# -*- coding: utf-8 -*-
{
    'name': 'Construction Materials AI',
    'version': '19.0.2.0.0',
    'category': 'Construction',
    'summary': 'Gestión de bodega de materiales con asistente IA',
    'description': """
        Módulo para gestión de materiales de construcción con:
        - Control de inventario de materiales (integrado con stock nativo)
        - Asistente IA para consultas
        - Alertas de stock bajo
    """,
    'author': 'Raul Cid',
    'website': 'https://cidev.dev',
    'depends': ['base', 'mail', 'stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'data/uom_data.xml',
        'data/discuss_channel_data.xml',
        'data/demo_materials.xml',
        'views/product_template_views.xml',
        'views/res_config_settings_views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'post_init_hook': '_post_init_hook',
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
