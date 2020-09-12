# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VATReportConfig(models.Model):
    _name = 'account.foreign.exchange.report.config'
    _description = 'Configure Foreign Exchange Report'
    _order = "date desc"

    date = fields.Date(
        string='Date',
        required=True)

    group_ids = fields.Many2many(
        comodel_name='account.group',
        domain=[('parent_id', '=', False)],
        string='Groups')
    account_gain = fields.Many2one(
        comodel_name='account.account',
        string='Account Foreign Exchange Gain',
        required=True)

    account_loss = fields.Many2one(
        comodel_name='account.account',
        string='Account Foreign Exchange Loss',
        required=True)
