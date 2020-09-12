# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class HREmployeeCustom(models.Model):
    _inherit = 'hr.employee'

    eos_amount = fields.Float(
        string='End of Service',
        compute="_calculate_end_of_service",
        required=False)

    def _calculate_end_of_service(self):
        for rec in self:
            contract_list = self.env['hr.contract'].search([('employee_id', '=', rec.id)], order='date_start')
            if len(contract_list) == 0:
                rec.eos_amount = 0.0
                continue
            running_contract_list = self.env['hr.contract'].search(
                [('employee_id', '=', rec.id), ('state', '=', 'open')])
            if len(running_contract_list) == 0:
                rec.eos_amount = 0.0
            else:
                joining_date = contract_list[0].date_start
                end_date = date.today()
                wage = running_contract_list[0].wage
                number_of_days = self.env['hr.payslip'].days360(joining_date, end_date)
                rec.eos_amount = ((wage * 21.0) / 365.0) * 12.0 * ((number_of_days / 30.0) / 12.0)
