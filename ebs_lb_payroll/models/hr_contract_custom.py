# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class ContractInherit(models.Model):
    _inherit = 'hr.contract'

    payroll_grade = fields.Selection(
        string='Payroll Grade',
        selection=[('1', 'Grade 1'),
                   ('2', 'Grade 2'), ('3', 'Grade 3')],
        required=False,related="job_id.payroll_grade" )

    package = fields.Monetary('Package',
                              default=0.0,
                              required=True,
                              tracking=True,
                              help="Employee's Package.")
    accommodation = fields.Monetary('Accommodation',
                                    default=0.0,
                                    required=True,
                                    tracking=True,
                                    help="Employee's Accommodation.")

    mobile_allowance = fields.Monetary('Mobile Allowance',
                                       default=0.0,
                                       required=True,
                                       tracking=True,
                                       )

    food_allowance = fields.Monetary('Food Allowance',
                                     default=0.0,
                                     required=True,
                                     tracking=True,
                                     )
    transport_allowance = fields.Monetary('Transport Allowance',
                                          default=0.0,
                                          required=True,
                                          tracking=True,
                                          )
    wage_rate = fields.Float(
        string='Wage Rate',
        default=60,
        required=True)

    @api.constrains('wage_rate')
    def _check_payment_date(self):
        for record in self:
            if record.wage_rate > 100 or record.wage_rate < 0:
                raise ValidationError(_("Rate Must be between 0 and 100"))

    @api.onchange('package', 'wage_rate')
    def calculate_wage(self):
        if self.package and self.wage_rate:
            if self.package != 0.0 and self.wage_rate != 0.0:
                temp_wage = (self.package * self.wage_rate) / 100.0
                self.wage = temp_wage
                self.accommodation = self.package - temp_wage

    @api.onchange('wage')
    def _calculate_wage(self):
        if self.package and self.wage:
            if self.package != 0.0 and self.wage != 0.0:
                self.accommodation = self.package - self.wage
