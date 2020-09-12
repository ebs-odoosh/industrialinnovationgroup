# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError

Marital_Status = [('single', 'Single'),
                  ('married', 'Married'),
                  ('cohabitant', 'Legal Cohabitant'),
                  ('widower', 'Widower'),
                  ('divorced', 'Divorced')]


class RecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    generate_contract = fields.Boolean('Generate Contract')
    create_employee = fields.Boolean('Create Employee')


class ApplicantChildrens(models.Model):
    _name = "hr.applicant.children"

    name = fields.Char('Children Name')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender')
    age = fields.Integer('Age')
    related_applicant = fields.Many2one('hr.applicant', 'Applicant')


class ApplicantSurveys(models.Model):
    _name = "hr.applicant.survey"

    response_id = fields.Many2one('survey.user_input', "Response", ondelete="set null")
    user_id = fields.Many2one(related="response_id.create_uid")
    related_survey = fields.Many2one(related="related_applicant.survey_id")
    related_applicant = fields.Many2one('hr.applicant', 'Related Applicant', ondelete="cascade")

    def action_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if self.env.user.id != self.user_id.id:
            raise UserError("Only survey owner can modified")
        if not self.response_id:
            response = self.related_survey._create_answer(partner=self.related_applicant.partner_id)
            self.response_id = response.id
        else:
            response = self.response_id
        # grab the token of the response and start surveying
        return self.related_survey.with_context(survey_token=response.token).action_start_survey()

    def action_print_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        if not self.response_id:
            return self.related_survey.action_print_survey()
        else:
            response = self.response_id
            return self.related_survey.with_context(survey_token=response.token).action_print_survey()


class Applicant(models.Model):
    _inherit = "hr.applicant"

    related_generate_contract = fields.Boolean(related='stage_id.generate_contract')
    related_create_employee = fields.Boolean(related='stage_id.create_employee')

    proposed_contracts = fields.One2many('hr.contract', 'applicant_id', string="Proposed Contracts",
                                         domain="[('company_id', '=', company_id)]")
    proposed_contracts_count = fields.Integer(compute="_compute_proposed_contracts_count",
                                              string="Proposed Contracts Count")

    response_ids = fields.One2many('hr.applicant.survey', 'related_applicant', "Responses")

    currency = fields.Many2one('res.currency', 'Currency', default=lambda x: x.env.company.currency_id)
    nationality = fields.Many2one('res.country', 'Nationality (Country)')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender')
    national_service = fields.Boolean('Nation Service Completed')
    currently_employed = fields.Boolean('Currently Employed')
    date_of_birth = fields.Date('Date Of Birth')
    last_position = fields.Char('Last Position')
    current_employer = fields.Char('Current Employer')
    current_location = fields.Char('Current location')
    total_years_of_exp = fields.Integer('Total Years of Exp')
    educational_background = fields.Text('Educational Background')
    marital_status = fields.Selection(Marital_Status, 'Marital Status')
    related_children = fields.One2many('hr.applicant.children', 'related_applicant', string="Children")
    current_salary = fields.Float("Current Salary")
    willing_relocate = fields.Boolean('Willing to Relocate')
    notice_period = fields.Float("Notice Period")
    other_offers = fields.Text("Any other Interviews or Offers ?")
    hiring_date = fields.Date('Hiring Confirmation Date')
    availability = fields.Date("Effective Start Date",
                               help="The date at which the applicant will be available to start working")

    def action_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if self.env.user not in self.response_ids.mapped("create_uid"):
            response = self.survey_id._create_answer(partner=self.partner_id)
            self.response_ids = [(0, 0, {'response_id': response.id})]
        else:
            line = self.response_ids.filtered(lambda x: x.create_uid.id == self.env.user.id)
            response = line.response_id
        # grab the token of the response and start surveying
        return self.survey_id.with_context(survey_token=response.token).action_start_survey()

    def action_print_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        if not self.response_ids:
            return self.survey_id.action_print_survey()
        else:
            response = self.response_ids.filtered(lambda x: x.create_uid.id == self.env.user.id).response_id
            return self.survey_id.with_context(survey_token=response.token).action_print_survey()

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        for rec in self:
            if rec.stage_id.create_employee == True:
                rec.hiring_date = fields.Date.today()

    def action_show_proposed_contracts(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.contract",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["applicant_id", "=", self.id], '|', ["active", "=", False], ["active", "=", True]],
            "name": "Proposed Contracts",
            "context": {'default_employee_id': self.emp_id.id},
        }

    def _compute_proposed_contracts_count(self):
        Contracts = self.env['hr.contract'].sudo()
        for applicant in self:
            applicant.proposed_contracts_count = Contracts.with_context(active_test=False).search_count([
                ('applicant_id', '=', applicant.id)])


class HrContract(models.Model):
    _inherit = 'hr.contract'

    applicant_id = fields.Many2one('hr.applicant',
                                   domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
