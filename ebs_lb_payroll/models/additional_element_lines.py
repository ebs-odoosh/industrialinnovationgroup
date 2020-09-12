# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class AdditionalElementLines(models.Model):
    _name = 'ebspayroll.additional.element.lines'
    _description = 'Additional Element Lines'

    additional_element_id = fields.Integer(
        string='Addition Element',
        required=True)

    employee = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=True)

    amount = fields.Float(
        string='Amount',
        required=True)

    _sql_constraints = [
        ('add_element_line_emp_unique', 'unique(employee,additional_element_id)', _("Employee already exists"))
    ]