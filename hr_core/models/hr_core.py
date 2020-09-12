# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrCompensationPayComponent(models.Model):
    _name = 'hr.compensation.pay.component'

    name = fields.Char('Name')
    code = fields.Char('Code')
    description = fields.Char('Description')


class HrCompensation(models.Model):
    _name = 'hr.compensation'

    name = fields.Many2one('hr.compensation.pay.component', 'Pay Component')
    code = fields.Char(related='name.code', string='Code')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    amount = fields.Float('Amount', default=0.0)
    currency = fields.Many2one('res.currency', default=lambda x: x.env.company.currency_id)
    frequency = fields.Integer('Frequency')
    is_payroll = fields.Boolean('Is Payroll Element')
    value = fields.Char('Value (If not Payroll)')
    period = fields.Selection([('daily', 'Daily'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], 'Period')
    related_job_position = fields.Many2one('hr.job', 'Related Job', copy=False)
    related_contract = fields.Many2one('hr.contract', 'Related Contract')
    component_description = fields.Char(
        string='Component Description',
        related='name.description')


class CostCenter(models.Model):
    _name = 'hr.cost.center'

    name = fields.Char("Cost Center", store=True)
    code = fields.Char("Code", required=True)
    related_department = fields.Many2one('hr.department', "Related Department", ondelete='set null')

    # @api.depends('code', 'related_department')
    # def _get_custom_name(self):
    #     for rec in self:
    #         if rec.code and rec.related_department:
    #             rec.name = ("%s - %s" % (rec.code, rec.related_department.name))
    #         else:
    #             rec.name = "Draft"


class HrJobTitle(models.Model):
    _name = 'job.title'

    name = fields.Char('Name')
    arabic_name = fields.Char('Arabic Name')


class HrJobGrade(models.Model):
    _name = 'job.grade'

    name = fields.Char('Job Grade')
    level = fields.Integer('Job Grade Level')
    related_compensations = fields.Many2many('hr.compensation.pay.component', string='Related Compensations')
    notice_period = fields.Integer('Notice Period (Days)', default=30)
    probation_period = fields.Integer('Probation Period (Days)', default=30)


department_types = [('BU', 'Group'), ('BD', 'Department'), ('BS', 'Section'),
                    ('SS', 'Subsection'), ]


class Department(models.Model):
    _inherit = "hr.department"

    type = fields.Selection(department_types, string='Type', default='BU')
    code = fields.Char('Code')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')

    @api.model
    def create(self, vals):
        res = super(Department, self).create(vals)
        if res.type == 'BU':
            res.code = self.env['ir.sequence'].next_by_code('business.unit')
        if res.type == 'BD':
            res.code = self.env['ir.sequence'].next_by_code('business.department')
        if res.type == 'BS':
            res.code = self.env['ir.sequence'].next_by_code('business.section')
        if res.type == 'SS':
            res.code = self.env['ir.sequence'].next_by_code('sub.section')
        return res


class IscoCode(models.Model):
    _name = "hr.isco.code"

    name = fields.Char('Label')
    code = fields.Char('Code')

    def name_get(self):
        names = []
        for record in self:
            names.append((record.id, "%s - %s" % (record.code, record.name)))
        return names


class Job(models.Model):
    _inherit = "hr.job"
    _description = "Job Position"

    name = fields.Char(string='Job Position', required=False, index=True, store=True)
    position_status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], default='active')
    job_grade = fields.Many2one('job.grade', string='Job Grade')
    job_title = fields.Many2one('job.title', string='Job Title')
    default_manager = fields.Many2one('hr.employee', 'Default Manager')
    group = fields.Many2one('hr.department', string='Group', domain=[('type', '=', 'BU')])
    department_id = fields.Many2one('hr.department', string='Department', domain=[('type', '=', 'BD')])
    section = fields.Many2one('hr.department', string='Section', domain=[('type', '=', 'BS')])
    subsection = fields.Many2one('hr.department', string='Subsection', domain=[('type', '=', 'SS')])
    related_compensations = fields.One2many('hr.compensation', 'related_job_position', string='Related Compensations')
    isco_code = fields.Many2one('hr.isco.code', 'ISCO Code')
    cost_center = fields.Many2one('hr.cost.center', string="Cost Center")
    state = fields.Selection([
        ('recruit', 'Recruitment in Progress'),
        ('open', 'Not Recruiting')
    ], string='Status', readonly=False, required=True, tracking=True, copy=False, default='recruit',
        help="Set whether the recruitment process is open or closed for this job position.")

    related_jobs = fields.One2many('hr.contract', 'job_id', 'Related Jobs')

    _sql_constraints = [
        ('name_company_uniq', 'check(1=1)',
         'The name of the job position must be unique per department in company!'),
    ]

    @api.onchange('group')
    def _on_group_change(self):
        if self.group:
            # self.department = False
            # self.section = False
            # self.subsection = False
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

    @api.onchange('department_id')
    def _on_department_change(self):
        if self.department_id:
            # self.section = False
            # self.subsection = False
            return {'domain': {
                'section': [('type', '=', 'BS'),
                            ('parent_id', 'child_of',
                             self.department_id.id)],
                'subsection': [('type', '=', 'SS'),
                               ('parent_id', 'child_of', self.department_id.id)]}}
        elif self.group:
            return self._on_group_change()
        else:
            return {'domain': {
                'section': [('type', '=', 'BS')],
                'subsection': [('type', '=', 'SS')]}}

    @api.onchange('section')
    def _on_section_change(self):
        if self.section:
            # self.subsection = False
            return {'domain': {
                'subsection': [('type', '=', 'SS'),
                               ('parent_id', 'child_of', self.section.id)]}}
        elif self.department_id:
            return self._on_department_change()
        else:
            return {'domain': {
                'subsection': [('type', '=', 'SS')]}}

    @api.onchange('job_grade')
    def onchange_job_grade(self):
        if not self.related_jobs:
            lines = [(5, 0, 0)]
            if self.job_grade:
                for compensations in self.job_grade.related_compensations:
                    lines.append((0, 0, {'name': compensations}))
            self.related_compensations = lines

    @api.model
    def create(self, vals):
        vals.update({'name': self.env['ir.sequence'].next_by_code('job.position')})
        result = super(Job, self).create(vals)
        default_signatures = self.env['hr.job.default.signature'].search([])
        for signature in default_signatures:
            result.write({
                'required_signatures': [(0, 0, {
                    'sequence': signature.sequence,
                    'name': signature.name.id
                })]
            })
        return result

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        return super(Job, self).copy(default=default)
