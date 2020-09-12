# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta
from calendar import monthrange


class AllowanceRequest(models.Model):
    _name = 'ebs.payroll.allowance.request'
    _description = 'Allowance Request'
    _order = "request_date desc"

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=True)

    request_type = fields.Many2one(
        comodel_name='ebs.payroll.allowance.request.type',
        string='Type',
        required=True)
    amount = fields.Float(
        string='Amount',
        required=True)
    request_date = fields.Date(
        string='Request Date',
        required=True, default=date.today())
    payment_date = fields.Date(
        string='Payment Date',
        required=False)
    amortization_start_date = fields.Date(
        string='Amortization Start Date',
        required=False)
    number_of_month = fields.Integer(
        string='Number of Month',
        required=False)

    description = fields.Text(
        string="Description",
        required=False)
    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'),
                   ('submit', 'Submitted'),
                   ('approved', 'Approved'),
                   ('reject', 'Rejected'),
                   ],
        required=False, default='draft')

    lines_ids = fields.One2many(
        comodel_name='ebs.payroll.allowance.request.lines',
        inverse_name='parent_id',
        string='Lines',
        required=False)

    def submit_request(self):
        self.state = 'submit'

    def accept_request(self):
        if not self.payment_date:
            raise ValidationError(_("Missing Payment Date"))
        if not self.amortization_start_date:
            raise ValidationError(_("Missing amortization date"))
        if not self.number_of_month:
            raise ValidationError(_("Missing number of month"))

        divide_by = round(self.number_of_month * (365 / 12))
        total = 0.0
        for x in range(self.number_of_month):
            line_date = self.amortization_start_date + relativedelta(months=x)
            days = monthrange(line_date.year, line_date.month)[1]
            if x != (self.number_of_month - 1):
                payment = (self.amount / divide_by) * days
                total += payment
            else:
                payment = self.amount - total

            self.env['ebs.payroll.allowance.request.lines'].create({
                'parent_id': self.id,
                'date': line_date,
                'amount': payment
            })

            self.state = 'approved'

    def reject_request(self):
        self.state = 'reject'

    def draft_request(self):
        self.state = 'draft'


class AllowanceRequestlines(models.Model):
    _name = 'ebs.payroll.allowance.request.lines'
    _description = 'Allowance Request lines'

    parent_id = fields.Many2one(
        comodel_name='ebs.payroll.allowance.request',
        string='Request',
        required=False)
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=False, related='parent_id.employee_id')

    parent_state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'),
                   ('submit', 'Submitted'),
                   ('approved', 'Approved'),
                   ('reject', 'Rejected'),
                   ],
        required=False, related='parent_id.state')

    date = fields.Date(
        string='Date',
        required=False)

    amount = fields.Float(
        string='Amount',
        required=False)
