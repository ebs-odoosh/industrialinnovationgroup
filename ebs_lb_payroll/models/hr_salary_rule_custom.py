# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SalaryRules(models.Model):
    _inherit = 'hr.salary.rule'






    istaxable = fields.Boolean(
        string='Is Taxable',
        required=False)
    template = fields.Selection(
        string='Template',
        selection=[
            ('AE', 'Additional Element'),
            ('package', 'Package Amount'),
            ('basic', 'Basic Amount'),
            ('gross', 'Gross Amount'),
            ('net', 'Net Amount'),
            ('ded', 'Deductions Amount'),
            ('acc', 'Accommodation Amount'),
            ('trns', 'Transport Amount'),
            ('mobile', 'Mobile Amount'),
            ('food', 'Food Amount'),
            ('eos', 'End Of Service'),
            ('rap', 'Request for Allowance Payment'),
            ('aap', 'Allowance Amortization Payment'),
        ],
        required=False, )
    related_element_type = fields.Many2one(
        comodel_name='ebspayroll.additional.element.types',
        string='Additional Element Type',
        required=False)


    # @api.depends('template')
    @api.onchange('template')
    def _template_onchange(self):
        payslip = True
        taxable = False
        condition = 'none'
        amount_type = 'code'
        code = ""
        if self.template == 'net':
            code = "result =  categories.ALW + categories.DED"
            payslip = True

        if self.template == 'package':
            code = "result = contract.package"
            payslip = True

        if self.template == 'acc':
            code = "result = contract.accommodation"
            payslip = True

        if self.template == 'basic':
            # code = "result = payslip.paid_amount"
            code = "result = contract.wage"
            payslip = True

        if self.template == 'trns':
            code = "result = contract.transport_allowance"
            payslip = True

        if self.template == 'food':
            code = "result = contract.food_allowance"
            payslip = True

        if self.template == 'mobile':
            code = "result = contract.mobile_allowance"
            payslip = True
            # taxable = True

        if self.template == 'ded':
            code = "result = categories.DED"
            payslip = True
            # taxable = True

        if self.template == 'gross':
            code = "result =  categories.ALW"
            payslip = True

        if self.template == 'rap':
            code = "result=payslip.env['hr.payslip'].calculateAllowancePayment(payslip,employee)"
            payslip = True
        if self.template == 'aap':
            code = "result=payslip.env['hr.payslip'].calculateAmortizationPayment(payslip,employee)"
            payslip = True

        if self.template == 'eos':
            code = "result=payslip.env['hr.payslip'].calculateEndOfService(payslip,employee)"
            payslip = True
        # if self.template == 'TRAN':
        #     code = "result=payslip.env['hr.payslip'].calculateTransportation(payslip,employee)"
        #     payslip = True
        if self.template == 'AE':
            code = ""
            payslip = True
        self.appears_on_payslip = payslip
        self.istaxable = taxable
        self.condition_select = condition
        self.amount_select = amount_type
        self.amount_python_compute = code
        return

    @api.onchange('related_element_type')
    def _related_element_type_onchange(self):
        if self.related_element_type:
            rec_code = '' + self.related_element_type.code
            python_code = "result=payslip.env['hr.payslip'].calculateAdditionalElements(payslip,employee,'" + rec_code + "')"
            self.amount_python_compute = python_code
        return

    @api.constrains('template')
    def check_beneficiary_number(self):
        rules_list = []
        if self.template:
            if self.template == 'AE':
                if self.id:
                    rules_list = self.env['hr.salary.rule'].search(
                        [('template', '=', self.template), ('struct_id', '=', self.struct_id.id),
                         ('related_element_type', '=', self.related_element_type.id),
                         ('id', '!=', self.id)])
                else:
                    rules_list = self.env['hr.salary.rule'].search(
                        [('template', '=', self.template), ('struct_id', '=', self.struct_id.id)],
                        ('related_element_type', '=', self.related_element_type.id))
                if len(rules_list) != 0:
                    raise ValidationError(
                        _("Template,salary structure and additional element combination already exists"))
            else:
                if self.id:
                    rules_list = self.env['hr.salary.rule'].search(
                        [('template', '=', self.template), ('struct_id', '=', self.struct_id.id),
                         ('id', '!=', self.id)])
                else:
                    rules_list = self.env['hr.salary.rule'].search(
                        [('template', '=', self.template), ('struct_id', '=', self.struct_id.id)])
            if len(rules_list) != 0:
                raise ValidationError(_("Template and salary structure combination already exists"))
