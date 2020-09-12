from odoo import fields, models, api, _


class AccountGroupCustom(models.Model):

    _inherit = "account.group"
    name_en = fields.Char(
        string='Name English',

        required=False)
    name_fr = fields.Char(
        string='Name French',
        required=False)

    closing_account = fields.Many2one(
       comodel_name='account.account',
       string='Closing Account',
       required=False)
