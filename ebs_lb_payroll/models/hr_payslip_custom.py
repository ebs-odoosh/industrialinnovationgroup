# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from odoo.tools.misc import format_date
from odoo.tools import float_round, date_utils
from odoo.tools import float_compare, float_is_zero
import math

class PayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    # @api.onchange('employee_id')
    # def _onchange_employee_2(self):
    #     self.name = '%s - %s - %s' % (
    #         format_date(self.env, self.date_from, date_format="MMMM"),
    #         self.employee_id.name or '',
    #         format_date(self.env, self.date_from, date_format="y")
    #     )

    payroll_grade = fields.Selection(
        string='Payroll Grade',
        selection=[('1', 'Grade 1'),
                   ('2', 'Grade 2'), ('3', 'Grade 3')],
        required=False, related="contract_id.job_id.payroll_grade")

    def days360(self, start_date, end_date, method_eu=False):
        start_day = start_date.day
        start_month = start_date.month
        start_year = start_date.year
        end_day = end_date.day
        end_month = end_date.month
        end_year = end_date.year

        if (
                start_day == 31 or
                (
                        method_eu is False and
                        start_month == 2 and (
                                start_day == 29 or (
                                start_day == 28 and
                                start_date.is_leap_year is False
                        )
                        )
                )
        ):
            start_day = 30

        if end_day == 31:
            if method_eu is False and start_day != 30:
                end_day = 1

                if end_month == 12:
                    end_year += 1
                    end_month = 1
                else:
                    end_month += 1
            else:
                end_day = 30

        return (
                end_day + end_month * 30 + end_year * 360 -
                start_day - start_month * 30 - start_year * 360)

    def calculateEndOfService(self, payslip, employee):
        contract_list = self.env['hr.contract'].search([('employee_id', '=', employee.id)], order='date_start')
        joining_date = contract_list[0].date_start
        end_date = payslip.contract_id.date_end
        wage = payslip.contract_id.wage
        number_of_days = self.days360(joining_date, end_date)
        eos_amount = ((wage * 21.0) / 365.0) * 12.0 * ((number_of_days / 30.0) / 12.0)
        return eos_amount

    def calculateAdditionalElements(self, payslip, employee, type_code):
        amount = 0.0
        elementTypeList = self.env['ebspayroll.additional.element.types'].search([('code', '=', type_code)])
        if len(elementTypeList) == 0:
            # raise ValidationError(_("There no element type with code %s", (type_code)))
            return 0.0
        elementType = elementTypeList[0]
        elementList = self.env['ebspayroll.additional.elements'].search(
            [('type', '=', elementType.id), ('payment_date', '>=', payslip.date_from),
             ('payment_date', '<=', payslip.date_to)])
        if len(elementList) == 0:
            # raise ValidationError(_("There no element  with Type %s", (type_code)))
            return 0.0

        for element in elementList:
            for rec in element.lines:
                if rec.employee.id == employee.id:
                    if elementType.type == 'D':
                        amount += (rec.amount * -1)
                    else:
                        amount += rec.amount
                    break
        return amount

    def calculateTransportation(self, payslip, employee):
        amount = 0.0

        ruleList = self.env['ebspayroll.transportation.rule'].search(
            [('payment_date', '>=', payslip.date_from),
             ('payment_date', '<=', payslip.date_to)])
        if len(ruleList) == 0:
            # raise ValidationError(_("There no element  with Type %s", (type_code)))
            return 0.0

        for rule in ruleList:
            for rec in rule.lines:
                if rec.employee.id == employee.id:
                    amount += (rec.amount * rec.days)
                    break
        return amount

    def calculateAllowancePayment(self, payslip, employee):
        amount = 0.0
        req_allowance = self.env['ebs.payroll.allowance.request'].search([('employee_id', '=', employee.id),
                                                                          ('state', '=', 'approved'),
                                                                          ('payment_date', '>=', payslip.date_from),
                                                                          ('payment_date', '<=', payslip.date_to)])
        for req in req_allowance:
            amount += req.amount
        return amount

    def calculateAmortizationPayment(self, payslip, employee):
        amount = 0.0
        req_line_allowance = self.env['ebs.payroll.allowance.request.lines'].search([('employee_id', '=', employee.id),
                                                                                ('parent_state', '=', 'approved'),
                                                                                ('date', '>=', payslip.date_from),
                                                                                ('date', '<=', payslip.date_to)])
        for line in req_line_allowance:
            amount += line.amount
        return amount

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        self.company_id = employee.company_id
        if not self.contract_id or self.employee_id != self.contract_id.employee_id:  # Add a default contract if not already defined
            contracts = employee._get_contracts(date_from, date_to)

            if not contracts or not contracts[0].structure_type_id.default_struct_id:
                self.contract_id = False
                self.struct_id = False
                return
            self.contract_id = contracts[0]
            self.struct_id = contracts[0].structure_type_id.default_struct_id

        payslip_name = self.struct_id.payslip_name or _('Salary Slip')
        self.name = '%s - %s - %s' % (
            format_date(self.env, self.date_from, date_format="MMMM"),
            self.employee_id.name or '',
            format_date(self.env, self.date_from, date_format="y")
        )

        if date_to > date_utils.end_of(fields.Date.today(), 'month'):
            self.warning_message = _(
                "This payslip can be erroneous! Work entries may not be generated for the period from %s to %s." %
                (date_utils.add(date_utils.end_of(fields.Date.today(), 'month'), days=1), date_to))
        else:
            self.warning_message = False

        self.worked_days_line_ids = self._get_new_worked_days_lines()

    def action_payslip_done(self):
        """
            Generate the accounting entries related to the selected payslips
            A move is created for each journal and for each month.
        """
        res = super(PayslipInherit, self).action_payslip_done()
        precision = self.env['decimal.precision'].precision_get('Payroll')

        # Add payslip without run
        payslips_to_post = self.filtered(lambda slip: not slip.payslip_run_id)

        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_to_post |= run.slip_ids

        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

        # Map all payslips by structure journal and pay slips month.
        # {'journal_id': {'month': [slip_ids]}}
        slip_mapped_data = {
            slip.struct_id.journal_id.id: {fields.Date().end_of(slip.date_to, 'month'): self.env['hr.payslip']} for slip
            in payslips_to_post}
        for slip in payslips_to_post:
            slip_mapped_data[slip.struct_id.journal_id.id][fields.Date().end_of(slip.date_to, 'month')] |= slip

        for journal_id in slip_mapped_data:  # For each journal_id.
            for slip_date in slip_mapped_data[journal_id]:  # For each month.
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                date = slip_date
                move_dict = {
                    'narration': '',
                    'ref': date.strftime('%B %Y') + " - " + slip_mapped_data[journal_id][slip_date].employee_id.name,
                    'journal_id': journal_id,
                    'date': date,
                }

                for slip in slip_mapped_data[journal_id][slip_date]:
                    move_dict['narration'] += slip.number or '' + ' - ' + slip.employee_id.name or ''
                    move_dict['narration'] += '\n'
                    for line in slip.line_ids.filtered(lambda line: line.category_id):
                        amount = -line.total if slip.credit_note else line.total
                        if line.code == 'NET':  # Check if the line is the 'Net Salary'.
                            for tmp_line in slip.line_ids.filtered(lambda line: line.category_id):
                                if tmp_line.salary_rule_id.not_computed_in_net:  # Check if the rule must be computed in the 'Net Salary' or not.
                                    if amount > 0:
                                        amount -= abs(tmp_line.total)
                                    elif amount < 0:
                                        amount += abs(tmp_line.total)
                        if float_is_zero(amount, precision_digits=precision):
                            continue
                        debit_account_id = line.salary_rule_id.account_debit.id
                        credit_account_id = line.salary_rule_id.account_credit.id

                        if debit_account_id:  # If the rule has a debit account.
                            debit = amount if amount > 0.0 else 0.0
                            credit = -amount if amount < 0.0 else 0.0

                            existing_debit_lines = (
                                line_id for line_id in line_ids if
                                line_id['name'] == line.name
                                and line_id['account_id'] == debit_account_id
                                and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0)))
                            debit_line = next(existing_debit_lines, False)

                            if not debit_line:
                                debit_line = {
                                    'name': line.name,
                                    'partner_id': False,
                                    'account_id': debit_account_id,
                                    'journal_id': slip.struct_id.journal_id.id,
                                    'date': date,
                                    'debit': debit,
                                    'credit': credit,
                                    'analytic_account_id': line.salary_rule_id.analytic_account_id.id or slip.contract_id.analytic_account_id.id,
                                }
                                line_ids.append(debit_line)
                            else:
                                debit_line['debit'] += debit
                                debit_line['credit'] += credit

                        if credit_account_id:  # If the rule has a credit account.
                            debit = -amount if amount < 0.0 else 0.0
                            credit = amount if amount > 0.0 else 0.0
                            existing_credit_line = (
                                line_id for line_id in line_ids if
                                line_id['name'] == line.name
                                and line_id['account_id'] == credit_account_id
                                and (line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0)
                            )
                            credit_line = next(existing_credit_line, False)

                            if not credit_line:
                                credit_line = {
                                    'name': line.name,
                                    'partner_id': False,
                                    'account_id': credit_account_id,
                                    'journal_id': slip.struct_id.journal_id.id,
                                    'date': date,
                                    'debit': debit,
                                    'credit': credit,
                                    'analytic_account_id': line.salary_rule_id.analytic_account_id.id or slip.contract_id.analytic_account_id.id,
                                }
                                line_ids.append(credit_line)
                            else:
                                credit_line['debit'] += debit
                                credit_line['credit'] += credit

                for line_id in line_ids:  # Get the debit and credit sum.
                    debit_sum += line_id['debit']
                    credit_sum += line_id['credit']

                # The code below is called if there is an error in the balance between credit and debit sum.
                if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                    acc_id = slip.journal_id.default_credit_account_id.id
                    if not acc_id:
                        raise UserError(
                            _('The Expense Journal "%s" has not properly configured the Credit Account!') % (
                                slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_credit = next(existing_adjustment_line, False)

                    if not adjust_credit:
                        adjust_credit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': 0.0,
                            'credit': debit_sum - credit_sum,
                        }
                        line_ids.append(adjust_credit)
                    else:
                        adjust_credit['credit'] = debit_sum - credit_sum

                elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                    acc_id = slip.journal_id.default_debit_account_id.id
                    if not acc_id:
                        raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (
                            slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_debit = next(existing_adjustment_line, False)

                    if not adjust_debit:
                        adjust_debit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': credit_sum - debit_sum,
                            'credit': 0.0,
                        }
                        line_ids.append(adjust_debit)
                    else:
                        adjust_debit['debit'] = credit_sum - debit_sum

                # Add accounting lines in the move
                move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                move = self.env['account.move'].create(move_dict)
                for slip in slip_mapped_data[journal_id][slip_date]:
                    slip.write({'move_id': move.id, 'date': date})
        return res
