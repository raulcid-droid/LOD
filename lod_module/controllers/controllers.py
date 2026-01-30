# from odoo import http


# class LodModule(http.Controller):
#     @http.route('/lod_module/lod_module', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lod_module/lod_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('lod_module.listing', {
#             'root': '/lod_module/lod_module',
#             'objects': http.request.env['lod_module.lod_module'].search([]),
#         })

#     @http.route('/lod_module/lod_module/objects/<model("lod_module.lod_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lod_module.object', {
#             'object': obj
#         })

