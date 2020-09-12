# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class AdditionalElements(models.Model):
    _name = 'ebspayroll.additional.elements'
    _description = 'Additional Elements'
    _order = "payment_date desc"
    type = fields.Many2one(
        comodel_name='ebspayroll.additional.element.types',
        string='Element Type',
        required=True)

    rule_type = fields.Selection(
        string='Type',
        related="type.type",
        required=False, )

    name = fields.Char(
        string='Name', compute="compute_name",
        required=False)
    payment_date = fields.Date(
        string='Payment Date',
        required=True)
    description = fields.Text(
        string="Description",
        required=False)
    active = fields.Boolean(
        string='Active', default=True,
        required=False)
    lines = fields.One2many(
        comodel_name='ebspayroll.additional.element.lines',
        inverse_name='additional_element_id',
        string='Lines',
        required=False,
        copy=True)

    def copy(self, default=None):
        default = dict(default or {})
        default['payment_date'] = self.payment_date + relativedelta(months=1)
        return super(AdditionalElements, self).copy(default)

    @api.constrains('payment_date')
    def _check_payment_date(self):
        for record in self:
            if len(self.env['ebspayroll.additional.elements'].search(
                    [('type', '=', record.id),
                     ('payment_date', '=', record.payment_date),
                     ('active', '=', True),
                     ('id', '!=', record.id)])) > 0:
                raise ValidationError(_("Date already exists"))

    @api.depends('type')
    def compute_name(self):
        for rec in self:
            rec.name = rec.type.name
