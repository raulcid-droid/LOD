{
    'name': "Libro de Obras Digital (LOD)", 
    'summary': "Desarrollo práctico para soluciones constructivas",
    'description': """
        Práctica SellSide V01 - Gestión de costos y peajes.
    """,
    'author': "Raul Cid",
    'website': "https://cidev.dev",
    'category': 'Project',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        # 'security/ir.model.access.csv', # ¡No olvides activarlo cuando definas modelos!
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application': True, # Crucial para que aparezca en el menú de Apps
}
