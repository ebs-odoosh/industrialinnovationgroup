# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class HRLeaveTypeCustom(models.Model):
    _inherit = 'hr.leave.type'

    is_haj_leave = fields.Boolean(
        string='Is Hajj Leave', default=False,
        required=False)

    is_sick_leave = fields.Boolean(
        string='Is Sick Leave', default=False,
        required=False)

    additional_element_type_id = fields.Many2one(
        comodel_name='ebspayroll.additional.element.types',
        string='Additional Element Type',
        required=False)
