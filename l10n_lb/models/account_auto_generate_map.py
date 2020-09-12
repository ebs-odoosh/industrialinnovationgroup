# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountAutoGenerateMap(models.Model):
    _name = 'account.auto.generate.mapping'
    _description = 'Configure auto generation for contacts and  contacts accounts'

    type = fields.Selection([
        ('app', 'Account Payable Purchase and Services'),
        ('apa', 'Account Payable Asset'),
        ('apc', 'Account Payable Charges'),
        ('ar', 'Account Receivable'),
        ('vats', 'VAT Sales'),
        ('vatp', 'VAT Purchase and Service'),
        ('vata', 'VAT Asset'),
        ('vatc', 'VAT Charges'),
    ], string='Account For', required=True)

    related_account = fields.Many2one(
        comodel_name='account.group',
        string='Group',
        required=True)

    account_type = fields.Many2one(
        comodel_name='account.account.type',
        string='Account Type',
        required=True)

    start_number = fields.Char(
        string='Start Number',
        required=True)

    next_number = fields.Char(
        string='Next Number',
        required=True)

    @api.onchange('related_account')
    def account_onchange(self):
        self.next_number = self.related_account.code_prefix
        self.start_number = self.related_account.code_prefix
