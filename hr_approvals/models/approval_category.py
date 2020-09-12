# -*- coding: utf-8 -*-

from odoo import models, fields, api

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')]


class ApprovalSequence(models.Model):
    _name = 'approval.sequence'

    sequence = fields.Integer('Sequence', default=1)
    user_id = fields.Many2one('res.users', 'Approver')
    is_head_department_approver = fields.Boolean('Head of Department Approver')
    is_manager_approver = fields.Boolean('Manager Approver')
    related_category = fields.Many2one('approval.category', 'Related Category')
    approver_category = fields.Char(
        string='Approver Category',
        required=False)


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    requirer_document = fields.Selection(selection_add=[('no', "None")], string="Documents", default="no",
                                         required=True)
    has_vacancy_type = fields.Selection(CATEGORY_SELECTION, string="Vacancy Type", default="no", required=True)
    is_requisition_request = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string="Is Requisition Request", default="no", required=True)
    is_termination_request = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string="Is Termination Request", default="no", required=True)
    is_termination_extend_request = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string="Is Extend Termination Request", default="no", required=True)
    has_job_title = fields.Selection(CATEGORY_SELECTION, string="Job Title", default="no", required=True)
    has_group = fields.Selection(CATEGORY_SELECTION, string="Group", default="no", required=True)
    has_department = fields.Selection(CATEGORY_SELECTION, string="Department", default="no", required=True)
    has_section = fields.Selection(CATEGORY_SELECTION, string="Section", default="no", required=True)
    has_subsection = fields.Selection(CATEGORY_SELECTION, string="Subsection", default="no", required=True)
    has_related_employee_id = fields.Selection(CATEGORY_SELECTION, string="Employee", default="no", required=True)
    has_related_contract = fields.Selection(CATEGORY_SELECTION, string="Contract", default="no", required=True)
    has_grade = fields.Selection(CATEGORY_SELECTION, string="Grade", default="no", required=True)
    has_job_position = fields.Selection(CATEGORY_SELECTION, string="Job Position", default="no", required=True)
    has_job_desc = fields.Selection(CATEGORY_SELECTION, string="Job Desc", default="no", required=True)
    has_replacement_employee_id = fields.Selection(CATEGORY_SELECTION, string="Replacement Report", default="no",
                                                   required=True)
    has_resignation_date = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string="Resignation Date", default="no", required=True)
    has_contract_type = fields.Selection(CATEGORY_SELECTION, string="Contract Type", default="no", required=True)
    has_requisition_type = fields.Selection(CATEGORY_SELECTION, string="Requisition Type", default="no", required=True)
    managers_only = fields.Boolean('Managers only')
    is_head_department_approver = fields.Boolean(
        string="Employee's Head Of Department",
        help="Automatically add the Head Of Department as approver on the request.")

    approval_sequence = fields.One2many('approval.sequence', 'related_category', 'Approval Sequence')

    @api.onchange('is_head_department_approver', 'is_manager_approver', 'user_ids')
    def _approvers_onchange(self):
        for rec in self:
            c = 0
            results = [(5, 0, 0)]
            if rec.is_head_department_approver:
                c += 1
                results.append((0, 0, {'sequence': c, 'is_head_department_approver': True}))
            if rec.is_manager_approver:
                c += 1
                results.append((0, 0, {'sequence': c, 'is_manager_approver': True}))
            if rec.user_ids:
                for user in rec.user_ids:
                    c += 1
                    results.append((0, 0, {'sequence': c, 'user_id': user.id.origin if user.id.origin else user.id}))
            rec.approval_sequence = results
