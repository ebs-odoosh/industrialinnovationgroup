# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VATReportConfig(models.Model):
    _name = 'account.vat.report.config'
    _description = 'Configure VAT Report'
    _order = "sequence"
    name = fields.Char(
        string='Name',
        required=True)
    final_step = fields.Boolean(
        string='Final Step',
        required=False,
        default=False
    )
    sequence = fields.Integer(
        string='Sequence',
        required=True)
    group = fields.Many2one(
        comodel_name='account.group',
        string='Account Group',
        required=False)
    account = fields.Many2one(
        comodel_name='account.account',
        string='Closing Account',
        required=True)
