from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrHousingType(models.Model):
    _name = 'hr.housing.type'

    name = fields.Char('Types')


class HrHousingAttach(models.Model):
    _name = 'hr.housing.attachment'

    name = fields.Many2one('hr.housing.type', 'Name')

    attachment_ids = fields.Many2many(comodel_name="ir.attachment",
                                      relation="m2m_housing_attachments",
                                      column1="housing_id",
                                      column2="attachment_id",
                                      string="File"
                                      )
    related_housing = fields.Many2one('hr.housing', 'Related Housing')


class HrHousing(models.Model):
    _name = 'hr.housing'
    _description = 'Housing for employees'

    def get_default_attachments(self):
        # for rec in self:
        #     current_types = rec.attached_documents.mapped('name')
        # ('id', 'not in', current_types.ids)
        types = self.env['hr.housing.type'].search([])
        if types:
            result = []
            for type in types:
                result.append((0, 0, {'name': type.id, 'attachment_ids': None}))
            # rec.attached_documents = result
            return result

    def update_default_attachments(self):
        for rec in self:
            current_types = rec.attached_documents.mapped('name')
            types = self.env['hr.housing.type'].search([('id', 'not in', current_types.ids)])
            if types:
                result = []
                for type in types:
                    result.append((0, 0, {'name': type.id, 'attachment_ids': None}))
                rec.attached_documents = result

    state = fields.Selection([('pending', 'Pending Approval'), ('approved', 'Approved'), ('refuse', 'Refused')],
                             default='pending',
                             string="Approval State")
    from_date = fields.Date('From Date')

    to_date = fields.Date('to Date')
    housing_location = fields.Char("Location")
    housing_residential_type = fields.Selection([('nre', 'Non-Relative House'),
                                                 ('own', 'Owned House'),
                                                 ('rel', 'Relative House'),
                                                 ('ren', 'Rental House'),
                                                 ], default='nre',
                                                string="Residential Type")
    housing_ownership = fields.Char("Ownership")
    housing_utility_bill = fields.Char("Utility Bill")
    attached_documents = fields.One2many('hr.housing.attachment', 'related_housing', default=get_default_attachments,
                                         string="Documents")
    related_declaration_form = fields.Many2one('documents.document')
    #                                        domain=lambda self: [('res_id', '=', self.employee_id.id), (
    # 'res_model', '=', self.employee_id._name)])
    related_lease_contract = fields.Many2one('documents.document')
    yearly_rent_value = fields.Float("Yearly Rent Value")
    tawtheeq_number = fields.Char("Tawtheeq Number")
    currency_id = fields.Many2one(related='employee_id.contract_id.currency_id')
    wage = fields.Monetary(related='employee_id.contract_id.wage')
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=True)
    refuse_reason = fields.Text('Refuse Reason')

    def state_approve(self):
        self.refuse_reason = ""
        self.write({'state': 'approved'})
        msg = _('Housing ' + self.housing_ownership + ' Approved')
        self.employee_id.message_post(body=msg)

    def state_pending(self):
        self.write({'state': 'pending'})

    def state_refuse(self):
        if self.refuse_reason:
            self.write({'state': 'refuse'})
            msg = _('Housing ' + self.housing_ownership + ' Rejected. Rejection Reason: ' + self.refuse_reason)
            self.employee_id.message_post(body=msg)
        else:
            raise ValidationError('Must add refuse reason!')
