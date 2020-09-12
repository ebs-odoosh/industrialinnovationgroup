# -*- coding: utf-8 -*-
# from odoo import http


# class EbsCapstoneAccount(http.Controller):
#     @http.route('/ebs_capstone_account/ebs_capstone_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ebs_capstone_account/ebs_capstone_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ebs_capstone_account.listing', {
#             'root': '/ebs_capstone_account/ebs_capstone_account',
#             'objects': http.request.env['ebs_capstone_account.ebs_capstone_account'].search([]),
#         })

#     @http.route('/ebs_capstone_account/ebs_capstone_account/objects/<model("ebs_capstone_account.ebs_capstone_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ebs_capstone_account.object', {
#             'object': obj
#         })
