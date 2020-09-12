from odoo import fields, models, api, _
from odoo.exceptions import UserError

import datetime


class HrResignation(models.Model):
    _inherit = 'hr.resignation'

    related_approval = fields.Many2one('approval.request', 'Approval Request')
    start_date = fields.Datetime(related="related_approval.create_date", string='Start Date')
    end_date = fields.Date(related="related_approval.resignation_date", string='End Date')


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    def _get_default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=',
                                                self.env.user.id)],
                                              limit=1)

    vacancy_type = fields.Selection([('internal', 'Internal'), ('external', 'External')],
                                    string='Vacancy Process Type')
    job_desc = fields.Text('Job Description')
    replacement_employee_id = fields.Many2one('hr.employee', string='Replacing (Employee)')
    contract_type = fields.Selection([('open', 'Open'), ('contract', 'Contract')], string='Vacancy Type')
    requisition_type = fields.Selection([('replace', 'Replacement'), ('new', 'New Requirement')],
                                        string='Requisition Type')
    can_create_job = fields.Boolean('Create Job', compute='_create_job', default=False, store=True)
    can_create_resign = fields.Boolean('Create Resign', compute='_create_resign', default=False, store=True)
    can_extend_resign = fields.Boolean('Extend Resign', compute='_extend_resign', default=False, store=True)
    related_job = fields.One2many('hr.job', 'related_requisition', string='Related Jobs')
    is_head_department_approver = fields.Boolean(related="category_id.is_head_department_approver")

    related_resign_request = fields.Many2one('hr.resignation', string='Resign Request')
    related_resign_date = fields.Date(related='related_resign_request.end_date', string='Request Original Date')
    extend_till = fields.Date('Extend Till')
    direct_employee_id = fields.Many2one('hr.employee', string='Related Employee',
                                         compute='_get_direct_employee', store=True)

    related_employee_id = fields.Many2one('hr.employee', string='Employee',
                                          default=_get_default_employee)
    related_contract = fields.Many2one('hr.contract', "Related Contract")
    resignation_date = fields.Date('Resignation Date')
    grade = fields.Many2one('job.grade', 'Grade')
    job_position = fields.Many2one('hr.job', 'Job Position')
    job_title = fields.Many2one('job.title', 'Job Title')
    group = fields.Many2one('hr.department', string='Group', domain=[('type', '=', 'BU')])
    department = fields.Many2one('hr.department', string='Department', domain=[('type', '=', 'BD')])
    section = fields.Many2one('hr.department', string='Section', domain=[('type', '=', 'BS')])
    subsection = fields.Many2one('hr.department', string='Subsection', domain=[('type', '=', 'SS')])
    approval_date = fields.Datetime(
        string='Approval Date',
        required=False,
        readonly=True)

    @api.depends('request_owner_id')
    def _get_direct_employee(self):
        for rec in self:
            employee = self.env['hr.employee'].search([('user_id', '=',
                                             rec.request_owner_id.id)],
                                           limit=1)
            rec.direct_employee_id = employee.id

    @api.onchange('request_owner_id')
    def onchange_project_id(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=',
                                                            self.env.user.id)],
                                                          limit=1)
        if current_employee:
            children = current_employee.child_ids
            return {'domain': {
                'related_employee_id': ['|', ('id', 'in', children.ids), ('id', '=', current_employee.id)]
            }}

    @api.onchange('related_resign_request')
    def onchange_related_resign_request(self):
        for rec in self:
            rec.extend_till = rec.related_resign_request.end_date

    @api.onchange('related_employee_id')
    def onchange_employee(self):
        if self.related_employee_id:
            self.related_contract = self.related_employee_id.contract_id
            self.job_position = self.related_employee_id.job_id
            self.job_title = self.related_employee_id.contract_id.job_title
            self.grade = self.related_employee_id.contract_id.job_grade
            days = self.grade.notice_period if self.grade else 30
            self.resignation_date = fields.Date.today() + datetime.timedelta(
                days=days)
            self.group = self.related_employee_id.contract_id.group
            self.department = self.related_employee_id.contract_id.department
            self.section = self.related_employee_id.contract_id.section
            self.subsection = self.related_employee_id.contract_id.subsection

    @api.model
    def create(self, vals):
        res = super(ApprovalRequest, self).create(vals)
        if res.is_termination_request == 'yes':
            res.related_contract = res.related_employee_id.contract_id
            res.job_position = res.related_employee_id.job_id
            res.job_title = res.related_employee_id.contract_id.job_title
            res.grade = res.related_employee_id.contract_id.job_grade
            days = res.grade.notice_period if res.grade else 30
            res.resignation_date = fields.Date.today() + datetime.timedelta(
                days=days)
            res.group = res.related_employee_id.contract_id.group
            res.department = res.related_employee_id.contract_id.department
            res.section = res.related_employee_id.contract_id.section
            res.subsection = res.related_employee_id.contract_id.subsection
        return res

    def write(self, vals):
        res = super(ApprovalRequest, self).write(vals)
        if vals.get(
                'related_employee_id') and self.is_termination_request == 'yes':
            self.related_contract = self.related_employee_id.contract_id
            self.job_position = self.related_employee_id.job_id
            self.job_title = self.related_employee_id.contract_id.job_title
            self.grade = self.related_employee_id.contract_id.job_grade
            days = self.grade.notice_period if self.grade else 30
            self.resignation_date = fields.Date.today() + datetime.timedelta(
                days=days)
            self.group = self.related_employee_id.contract_id.group
            self.department = self.related_employee_id.contract_id.department
            self.section = self.related_employee_id.contract_id.section
            self.subsection = self.related_employee_id.contract_id.subsection
        return res

    @api.onchange('job_title', 'related_employee_id')
    def compute_name_get(self):
        for request in self:
            if request.is_requisition_request == 'yes':
                if request.job_title:
                    request.name = request.category_id.name + " - " + request.job_title.name
                    continue
            elif request.is_termination_request == 'yes' or request.is_termination_extend_request == 'yes':
                if request.related_employee_id:
                    request.name = request.category_id.name + " - " + request.related_employee_id.name
                    continue
            request.name = request.category_id.name

    @api.onchange('category_id', 'request_owner_id')
    def _onchange_category_id(self):
        current_users = self.approver_ids.mapped('user_id')
        new_users = self.category_id.user_ids
        if self.category_id.is_manager_approver or self.category_id.is_head_department_approver:
            employee = self.env['hr.employee'].search([('user_id', '=', self.request_owner_id.id)], limit=1)
        if self.category_id.is_manager_approver:
            if employee.parent_id.user_id:
                new_users |= employee.parent_id.user_id
        if self.category_id.is_head_department_approver:
            if employee.department_id.manager_id.user_id:
                new_users |= employee.department_id.manager_id.user_id
        for user in new_users - current_users:
            sequence = 0
            if (self.category_id.is_manager_approver and user.id == employee.parent_id.user_id):
                sequence = self.category_id.approval_sequence.filtered(
                    lambda x: x.is_manager_approver == True).sequence
            elif (
                    self.category_id.is_head_department_approver and user.id == employee.department_id.manager_id.user_id):
                sequence = self.category_id.approval_sequence.filtered(
                    lambda x: x.is_head_department_approver == True).sequence
            elif user in self.category_id.approval_sequence.mapped('user_id'):
                sequence = self.category_id.approval_sequence.filtered(
                    lambda x: x.user_id.id == user.id).sequence
            approver_category = self.category_id.approval_sequence.filtered(
                lambda x: x.user_id.id == user.id).approver_category
            self.approver_ids += self.env['approval.approver'].new({
                'sequence': sequence,
                'user_id': user.id,
                'approver_category': approver_category,
                'request_id': self.id,
                'status': 'new'})

    @api.depends('request_status', 'is_requisition_request')
    def _create_job(self):
        for rec in self:
            if rec.request_status == 'approved' and rec.is_requisition_request == 'yes':
                rec.can_create_job = True
            else:
                rec.can_create_job = False

    @api.depends('request_status', 'is_termination_request')
    def _create_resign(self):
        for rec in self:
            resign = rec.env['hr.resignation'].search([('related_approval', '=', rec.id)])
            if rec.request_status == 'approved' and rec.is_termination_request == 'yes' and not resign:
                rec.can_create_resign = True
            else:
                rec.can_create_resign = False

    @api.depends('request_status', 'is_termination_extend_request')
    def _extend_resign(self):
        for rec in self:
            resign = rec.env['hr.resignation'].search([('related_approval', '=', rec.id)])
            if rec.request_status == 'approved' and rec.is_termination_extend_request == 'yes' and not resign:
                rec.can_extend_resign = True
            else:
                rec.can_extend_resign = False

    @api.onchange('group')
    def _on_group_change(self):
        if self.group:
            self.department = False
            self.section = False
            self.subsection = False
            return {'domain': {
                'department': [('type', '=', 'BD'),
                               ('parent_id', 'child_of', self.group.id)],
                'section': [('type', '=', 'BS'),
                            ('parent_id', 'child_of',
                             self.group.id)],
                'subsection': [('type', '=', 'SS'),
                               ('parent_id', 'child_of', self.group.id)]}}
        else:
            return {'domain': {'department': [('type', '=', 'BD')],
                               'section': [('type', '=', 'BS')],
                               'subsection': [('type', '=', 'SS')]}}

    @api.onchange('department')
    def _on_department_change(self):
        if self.department:
            self.section = False
            self.subsection = False
            return {'domain': {
                'section': [('type', '=', 'BS'),
                            ('parent_id', 'child_of',
                             self.department.id)],
                'subsection': [('type', '=', 'SS'),
                               ('parent_id', 'child_of', self.department.id)]}}
        elif self.group:
            return self._on_group_change()
        else:
            return {'domain': {
                'section': [('type', '=', 'BS')],
                'subsection': [('type', '=', 'SS')]}}

    @api.onchange('section')
    def _on_section_change(self):
        if self.section:
            self.subsection = False
            return {'domain': {
                'subsection': [('type', '=', 'SS'),
                               ('parent_id', 'child_of', self.section.id)]}}
        elif self.department:
            return self._on_department_change()
        else:
            return {'domain': {
                'subsection': [('type', '=', 'SS')]}}

    def action_confirm(self):
        if len(self.approver_ids) < self.approval_minimum:
            raise UserError(
                _("You have to add at least %s approvers to confirm your request.") % self.approval_minimum)
        if self.requirer_document == 'required' and not self.attachment_number:
            raise UserError(_("You have to attach at lease one document."))
        approvers = \
            self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new').sorted('sequence')[
                0]
        approvers._create_activity()
        approvers.write({'status': 'pending'})
        self.write({'date_confirmed': fields.Datetime.now()})

    def action_approve(self, approver=None):
        if not isinstance(approver, models.BaseModel):
            approver = self.mapped('approver_ids').filtered(
                lambda approver: approver.user_id == self.env.user
            )
        approver.write({'status': 'approved', 'approval_date': datetime.datetime.now()})
        self.sudo()._get_user_approval_activities(user=self.env.user).action_feedback()
        approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new').sorted(
            'sequence')

        if approvers:
            approvers[0]._create_activity()
            approvers[0].write({'status': 'pending'})
        else:
            self.approval_date = datetime.datetime.now()

    @api.depends('approver_ids.status')
    def _compute_request_status(self):
        for request in self:
            status_lst = request.mapped('approver_ids.status')
            minimal_approver = request.approval_minimum if len(status_lst) >= request.approval_minimum else len(
                status_lst)
            if status_lst:
                if status_lst.count('cancel'):
                    status = 'cancel'
                elif status_lst.count('refused'):
                    status = 'refused'
                elif status_lst.count('new') and not status_lst.count('pending'):
                    status = 'new'
                elif status_lst.count('approved') >= minimal_approver:
                    status = 'approved'
                else:
                    status = 'pending'
            else:
                status = 'new'
            request.request_status = status

    def _get_job_default_values(self):
        dict = {
            'default_group': self.group.id,
            'default_department_id': self.department.id,
            'default_section': self.section.id,
            'default_subsection': self.subsection.id,
            'default_related_requisition': self.id,
            'default_description': self.job_desc,
            'default_job_title': self.job_title.id,
        }
        dict.update(self._context)
        return dict

    def create_job_position(self):
        return {
            'name': 'Job Position',
            'view_mode': 'form',
            'res_model': 'hr.job',
            'type': 'ir.actions.act_window',
            'context': self._get_job_default_values(),
        }

    def _get_resign_default_values(self):
        dict = {
            'default_related_employee': self.related_employee_id.id,
            'default_related_contract': self.related_contract.id,
            'default_related_approval': self.id
        }
        dict.update(self._context)
        return dict

    def create_resignation(self):
        return {
            'name': 'Resignation',
            'view_mode': 'form',
            'res_model': 'hr.resignation',
            'type': 'ir.actions.act_window',
            'context': self._get_resign_default_values(),
        }

    def extend_resignation(self):
        # if self.related_resign_request.state != 'extended':
        self.related_resign_request.set_extend()
        res = self.env['hr.resignation'].create({
            'start_date': self.related_resign_request.start_date,
            'end_date': self.extend_till,
            'related_employee': self.related_resign_request.related_employee.id,
            'related_contract': self.related_resign_request.related_contract.id,
            'related_approval': self.id,
            'extended_from': self.related_resign_request.id,
        })
        self._extend_resign()
        res.set_active()

    has_vacancy_type = fields.Selection(related="category_id.has_vacancy_type")
    has_job_title = fields.Selection(related="category_id.has_job_title")
    has_group = fields.Selection(related="category_id.has_group")
    has_department = fields.Selection(related="category_id.has_department")
    has_section = fields.Selection(related="category_id.has_section")
    has_subsection = fields.Selection(related="category_id.has_subsection")
    has_job_desc = fields.Selection(related="category_id.has_job_desc")
    has_replacement_employee_id = fields.Selection(related="category_id.has_replacement_employee_id")
    has_contract_type = fields.Selection(related="category_id.has_contract_type")
    has_requisition_type = fields.Selection(related="category_id.has_requisition_type")
    has_related_employee_id = fields.Selection(related="category_id.has_related_employee_id")
    has_related_contract = fields.Selection(related="category_id.has_related_contract")
    has_grade = fields.Selection(related="category_id.has_grade")
    has_job_position = fields.Selection(related="category_id.has_job_position")
    has_resignation_date = fields.Selection(related="category_id.has_resignation_date")
    is_requisition_request = fields.Selection(related="category_id.is_requisition_request")
    is_termination_request = fields.Selection(related="category_id.is_termination_request")
    is_termination_extend_request = fields.Selection(related="category_id.is_termination_extend_request")


class ApprovalApprover(models.Model):
    _inherit = 'approval.approver'

    sequence = fields.Integer('Sequence', default=1)
    approver_category = fields.Char(
        string='Approver Category',
        required=False)
    approval_date = fields.Datetime(
        string='Approval Date',
        required=False, readonly=True)

    # @api.model
    # def create(self, vals):
    #     approval = super(ApprovalApprover, self).create(vals)
    #     approval.approval_date = datetime.datetime.now()
    #     return approval


class Job(models.Model):
    _inherit = "hr.job"
    _description = "Job Position"

    related_requisition = fields.Many2one('approval.request', string='Related Requisition')
    requisition_job_title = fields.Many2one(related="related_requisition.job_title")
    vacancy_type = fields.Selection(related="related_requisition.vacancy_type")
    contract_type = fields.Selection(related="related_requisition.contract_type")
    requisition_type = fields.Selection(related="related_requisition.requisition_type")
    replacement_employee_id = fields.Many2one(related="related_requisition.replacement_employee_id")
