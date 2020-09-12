from odoo import fields, models, api


class EmployeeColorCombo(models.Model):
    _name = 'employee.color.combo'

    name = fields.Many2one(
        comodel_name='color.class',
        string='Color Class',
        required=True)
    nationality_id = fields.Many2one(
        comodel_name='res.country',
        string='Nationality',
        required=False)
    group_id = fields.Many2one(
        comodel_name='hr.contract.group',
        string='Group',
        required=False)
    subgroup_id = fields.Many2one(
        comodel_name='hr.contract.subgroup',
        string='Subgroup',
        required=False)
    employment_type_id = fields.Many2one(
        comodel_name='hr.contract.employment.type',
        string='Employment Type',
        required=False)
