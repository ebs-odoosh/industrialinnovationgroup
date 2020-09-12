# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VATReport(models.Model):
    _name = 'account.vat.report'
    _description = "nothing to see here"

    name = fields.Char(
        string='Name',
        required=False)
