from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from lxml import etree
import json

Religions_list = [
    ('apostolic', 'Apostolic'),
    ('baptist', 'Baptist'),
    ('buddhist', 'Buddhist'),
    ('charismatic', 'Charismatic'),
    ('evang', 'Evang'),
    ('lutheran-church', 'Lutheran Church'),
    ('evangelical', 'Evangelical'),
    ('free-church-alzey', 'Free church Alzey'),
    ('free-religion-of-the-den', 'Free religion of the den'),
    ('french-reformed', 'French reformed'),
    ('hebrew-reg-baden', 'Hebrew reg. BADEN'),
    ('hebrew-reg-wuertbg', 'Hebrew reg. WUERTBG'),
    ('hebrew-state', 'Hebrew state'),
    ('hindu', 'Hindu'),
    ('islamic', 'Islamic'),
    ('israelite', 'Israelite'),
    ("jehovah-s-witness", "Jehovah's witness"),
    ('mennonite-church', 'Mennonite Church'),
    ('jewish', 'Jewish'),
    ('mennonite-church', 'Mennonite Church'),
    ('mormon', 'Mormon'),
    ('moravian-congregation', 'Moravian Congregation'),
    ('muslim', 'Muslim'),
    ('netherl', 'Netherl'),
    ('netherl-reformed-church', 'Netherl. Reformed Church'),
    ('new-apostolic', 'New apostolic'),
    ('no-denomination', 'No denomination'),
    ('old-catholic', 'Old Catholic'),
    ('oecumenic', 'Oecumenic'),
    ('protestant', 'Protestant'),
    ('roman-catholic', 'Roman Catholic'),
    ("shia-muslim", "Shi'a Muslim"),
    ('sunni-muslim', 'Sunni Muslim'),
    ('christian', 'Christian'),
    ('christian-reformed', 'Christian Reformed'),
]


class ContractEmploymentType(models.Model):
    _name = 'hr.contract.employment.type'

    name = fields.Char('Type')
    code = fields.Char('Prefix')
    related_sequence = fields.Many2one('ir.sequence', 'Related Sequence')


class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    title = fields.Many2one('res.partner.title')
    lang = fields.Many2one('res.lang', string='Native Language',
                           domain="['|',('active','=',True),('active','=',False)]")
    contract_employment_type = fields.Many2one('hr.contract.employment.type', 'Employment Type')
    id_generated = fields.Boolean('ID generated')
    strata_id = fields.Char('Strata ID')
    system_id = fields.Char('System ID')
    firstname = fields.Char('Firstname')
    middlename = fields.Char('Middlename')
    lastname = fields.Char('Lastname')
    arabic_name = fields.Char('Arabic Name')
    mothers_name = fields.Char("Mother's name")
    arabic_mothers_name = fields.Char("Arabic Mother's name")
    religion = fields.Selection(Religions_list, 'Religions')
    street = fields.Char('Street')
    po_box = fields.Char('PO-Box')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    parent_id = fields.Many2one(related='contract_id.manager_id', string='Manager', store=True, readonly=False)
    job_id = fields.Many2one(related='contract_id.job_id', store=True, string='Job Position')
    job_title = fields.Char(related='job_id.job_title.name', string='Job Title')
    department_id = fields.Many2one(related='contract_id.department_id', store=True, string="OC Path")

    dependents = fields.One2many('res.partner', 'related_employee', 'Dependents')

    notice_ids = fields.One2many('hr.notice', 'related_employee', 'Notices')

    state = fields.Selection([('pending', 'Pending Approval'), ('approved', 'Approved'), ('reject', 'Reject')],
                             default='pending',
                             string="Approval State")

    housing_ids = fields.One2many(
        comodel_name='hr.housing',
        inverse_name='employee_id',
        string='Housings',
        required=False)
    reject_reason = fields.Text('Reject Reason')

    read_only_user_role = fields.Boolean(compute='_get_user_group', default=False)
    all_model_read_only = fields.Boolean(compute='_get_user_group', default=False)
    invisible_user_role = fields.Boolean(compute='_get_user_group', default=False)

    @api.depends('read_only_user_role', 'invisible_user_role', 'all_model_read_only')
    def _get_user_group(self):
        for rec in self:
            user = self.env.user
            if user.has_group('base.user_admin'):
                rec.invisible_user_role = False
                rec.read_only_user_role = False
                rec.all_model_read_only = False

            elif user.has_group('security_rules.group_hr_employee') and (
                    (user.employee_ids.subordinate_ids and rec.id in user.employee_ids.subordinate_ids.ids) or (
                    rec.id == user.employee_ids.parent_id.id)):
                rec.invisible_user_role = True
                rec.read_only_user_role = True
                rec.all_model_read_only = True

            elif user.has_group('security_rules.group_hr_employee'):
                rec.read_only_user_role = True
                rec.invisible_user_role = False
                rec.all_model_read_only = False
            else:
                rec.all_model_read_only = False
                rec.read_only_user_role = False
                rec.invisible_user_role = False

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(HrEmployeePrivate, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                             submenu=submenu)
        if view_type == "form":
            doc = etree.XML(res['arch'])
            for field in res['fields']:
                for node in doc.xpath("//field[@name='%s']" % field):
                    node.set("readonly", "[('all_model_read_only','=',True)]")
                    modifiers = json.loads(node.get("modifiers"))
                    # if modifiers.get('readonly') and modifiers.get('readonly') != True:
                    # modifiers.get('readonly').append(['all_model_read_only', '=', True])
                    if not modifiers.get('readonly'):
                        modifiers['readonly'] = "[('all_model_read_only','=',True)]"
                    node.set("modifiers", json.dumps(modifiers))

            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    def split_code(self, code):
        return code.split(self.contract_employment_type.related_sequence.prefix, 1)[1]

    def generate_id(self):
        for rec in self:
            if rec.contract_employment_type.related_sequence:
                rec.strata_id = self.env['ir.sequence'].next_by_code(rec.contract_employment_type.related_sequence.code)
                rec.system_id = rec.contract_employment_type.code + self.split_code(rec.strata_id)
                rec.id_generated = True
            else:
                raise ValidationError('Select Employee Type Before!')

    @api.onchange('contract_employment_type')
    def onchange_contract_employment_type(self):
        for rec in self:
            rec.id_generated = False

    def state_approve(self):
        self.reject_reason = ""
        self.write({'state': 'approved'})
        msg = _('Employee Approved')
        self.message_post(body=msg)

    def state_pending(self):
        self.write({'state': 'pending'})

    def log_and_reject(self):
        self = self.sudo()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Reason',
            'res_model': 'log.note.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('hr_employee_custom.log_note_reject_wizard_view_form').id,
            'context': {
                'related_name': self._name,
            }
        }

    def state_reject(self):
        if self.reject_reason:
            self.write({'state': 'reject'})
            msg = _('Employee Rejected. Rejection Reason: ' + self.reject_reason)
            self.message_post(body=msg)
        else:
            raise ValidationError('Must add reject reason!')

    @api.onchange('firstname', 'middlename', 'lastname')
    def _onchange_name(self):
        for rec in self:
            if rec.firstname and rec.middlename and rec.lastname:
                rec.name = (rec.firstname or '') + ' ' + (rec.middlename or '') + ' ' + (rec.lastname or '')


class Partner(models.Model):
    _inherit = 'res.partner'

    related_employee = fields.Many2one('hr.employee', 'Related Employee')

    state = fields.Selection([('pending', 'Pending Approval'), ('approved', 'Approved'), ('reject', 'Reject')],
                             default='pending',
                             string="Approval State")

    reject_reason = fields.Text('Reject Reason')

    contact_relation_type_id = fields.Many2one(
        comodel_name='contact.relation.type',
        string='Relation Type',
        required=False)

    # def _audit_logs(self, vals):
    #     for rec in self:
    #         log = "Following Fields Changed:<br/>"
    #         # message_post(body=_(u'Shipment N° %s has been cancelled' % picking.carrier_tracking_ref))
    #         for val in vals:
    #             log = log + "   - " + self._fields[val].string + " <br/>"
    #         rec.message_post(body=log)

    # def write(self, vals):
    #     # self._audit_logs(vals)
    #     # if vals and len(vals) > 1 or not vals.get('state'):
    #     #     vals.update({'state': 'pending'})
    #     # res = super(Partner, self).write(vals)
    #
    #     return res

    def state_approve(self):
        self.reject_reason = ""
        self.write({'state': 'approved'})
        msg = _('Dependent ' + self.name + ' Approved')
        self.related_employee.message_post(body=msg)

    def state_pending(self):
        self.write({'state': 'pending'})

    def log_and_reject(self):
        self = self.sudo()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Reason',
            'res_model': 'log.note.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('hr_employee_custom.log_note_reject_wizard_view_form').id,
            'context': {
                'related_name': self._name,
            }
        }

    def state_reject(self):
        if self.reject_reason:
            self.write({'state': 'reject'})
            msg = _('Dependent ' + self.name + ' Rejected. Rejection Reason: ' + self.reject_reason)
            self.related_employee.message_post(body=msg)
        else:
            raise ValidationError('Must add reject reason!')
