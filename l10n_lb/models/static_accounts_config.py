# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VATReportConfig(models.Model):
    _name = 'account.static.accounts.config'
    _description = 'Configure Static Accounts'

    code = fields.Char(
        string='Code',
        required=True)

    name = fields.Char(
        string='Name',
        required=True)
