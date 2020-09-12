# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta
import calendar


class HRLeaveCustom(models.Model):
    _inherit = 'hr.leave'

    @api.model
    def create(self, vals):
        leave = super(HRLeaveCustom, self).create(vals)
        for rec in leave:
            if rec.holiday_status_id.is_haj_leave:
                start_date = date(rec.date_from.year, 1, 1)
                end_date = date(rec.date_from.year, 12, 31)
                leave_list = self.env['hr.leave'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('holiday_status_id', '=', rec.holiday_status_id.id),
                    ('date_from', '>=', start_date),
                    ('date_from', '<=', end_date),
                    ('state', '=', 'validate')
                ])
                if len(leave_list) > 0:
                    raise ValidationError(_("Cannot take 2 Haj Leave per year"))
        return leave

    def write(self, vals):
        leave = super(HRLeaveCustom, self).write(vals)
        if leave:
            if self.holiday_status_id.is_haj_leave:
                start_date = date(self.date_from.year, 1, 1)
                end_date = date(self.date_from.year, 12, 31)
                leave_list = self.env['hr.leave'].search([
                    ('id', '!=', self.id),
                    ('employee_id', '=', self.employee_id.id),
                    ('holiday_status_id', '=', self.holiday_status_id.id),
                    ('date_from', '>=', start_date),
                    ('date_from', '<=', end_date),
                    ('state', '=', 'validate')
                ])
                if len(leave_list) > 0:
                    raise ValidationError(_("Cannot take 2 Haj Leave per year"))
        return leave

    def action_approve(self):
        for rec in self:
            if rec.holiday_status_id.is_sick_leave:
                if rec.number_of_days > 1:
                    attachment_list = self.env['ir.attachment'].search(
                        [('res_model', '=', 'hr.leave'), ('res_id', '=', rec.id)])
                    if len(attachment_list) == 0:
                        additional_element_type = rec.holiday_status_id.additional_element_type_id
                        if additional_element_type:
                            deduction_days = rec.number_of_days - 1
                            contract = self.env['hr.contract'].search([
                                ('state', '=', 'open'), ('employee_id', '=', rec.employee_id.id)
                            ], limit=1)
                            if contract:
                                wage_day = contract.wage / 22.0
                                deduction_amount = deduction_days * wage_day
                                date_after_month = rec.date_from + relativedelta(months=1)
                                additional_element_list = self.env['ebspayroll.additional.elements'].search([
                                    ('type', '=', additional_element_type.id),
                                    ('payment_date', '<=', date(date_after_month.year, date_after_month.month, 1)),
                                    ('payment_date', '<=', date(date_after_month.year, date_after_month.month,
                                                                calendar.monthrange(date_after_month.year,
                                                                                    date_after_month.month)[1])),
                                ])
                                if len(additional_element_list) != 0:
                                    additional_element = additional_element_list[0]
                                else:
                                    additional_element = self.env['ebspayroll.additional.elements'].create({
                                        'type': additional_element_type.id,
                                        'payment_date': date(date_after_month.year, date_after_month.month, 1)
                                    })

                                line = self.env['ebspayroll.additional.element.lines'].search([
                                    ('employee', '=', rec.employee_id.id),
                                    ('additional_element_id', '=', additional_element.id)
                                ], limit=1)
                                if line:
                                    line.amount = line.amount + deduction_amount
                                else:
                                    self.env['ebspayroll.additional.element.lines'].create({
                                        'employee': rec.employee_id.id,
                                        'additional_element_id': additional_element.id,
                                        'amount': deduction_amount
                                    })
                            else:
                                raise ValidationError(_("Employee Dont Have a running contract"))
                        else:
                            raise ValidationError(_("Please add additional element type to sick leave"))
        return super(HRLeaveCustom, self).action_validate()
