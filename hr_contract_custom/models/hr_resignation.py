from odoo import fields, models, api


class HrResignation(models.Model):
    _name = 'hr.resignation'

    state = fields.Selection(
        [('draft', 'Draft'), ('active', 'Active'), ('done', 'Done'), ('extended', 'Resignation Extended'),
         ('cancel', 'Cancelled')],
        string='Status',
        readonly=True, required=True, tracking=True, copy=False, default='draft')
    name = fields.Char('Name', compute='get_employee_name')
    related_employee = fields.Many2one('hr.employee', string="Employee")
    related_contract = fields.Many2one('hr.contract', 'Contract', ondelete='cascade')
    extended_from = fields.Many2one('hr.resignation', 'Extended From', readonly=True)

    # can_do_survey = fields.Boolean('can do interview', compute="_can_do_survey")
    # can_approve_survey = fields.Boolean('can approve interview', compute="_can_approve_survey")
    # calculate_due_date = fields.Boolean('Cal', compute="_calculate_get_due_date")
    # due_date = fields.Integer('Due Date', compute="_get_due_date", store=True)

    @api.depends('related_employee')
    def get_employee_name(self):
        for rec in self:
            rec.name = rec.related_employee.name + ' Resignation'

    def set_done(self):
        self.write({'state': 'done'})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def set_cancel(self):
        self.write({'state': 'cancel'})
        self.related_contract.write(
            {'effective_end_date': self.related_contract.date_end})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def set_active(self):
        self.write({'state': 'done'})
        self.related_contract.write(
            {'effective_end_date': self.end_date})


    def set_extend(self):
        self.write({'state': 'extended'})
