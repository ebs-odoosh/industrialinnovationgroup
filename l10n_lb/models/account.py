from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = "account.account"

    name_en = fields.Char(
        string='Name English',

        required=False)
    name_fr = fields.Char(
        string='Name French',
        required=False)

    @api.depends('code')
    def _compute_account_root(self):
        # this computes the first 2 digits of the account.
        # This field should have been a char, but the aim is to use it in a side panel view with hierarchy, and it's only supported by many2one fields so far.
        # So instead, we make it a many2one to a psql view with what we need as records.
        for record in self:
            record.root_id = record.code and ord(record.code[0]) or False

    @api.model
    def create(self, vals):

        
        acc = super(AccountAccount, self).create(vals)
        if not acc.group_id:
            AccountGroup = self.env['account.group']
            group = False
            code_prefix = acc.code
            # find group with longest matching prefix
            while code_prefix:
                matching_group = AccountGroup.search([('code_prefix', '=', code_prefix)], limit=1)
                if matching_group:
                    group = matching_group
                    break
                code_prefix = code_prefix[:-1]
            acc.group_id = group
        return acc

    

    with_auxiliaries = fields.Boolean(
        string='Auxiliaries',
        default=False,
        help='Add the customer/vendor id into trial balance report.'
    )


class AccountAccountTemplate(models.Model):
    _inherit = "account.account.template"

    with_auxiliaries = fields.Boolean(
        string='Auxiliaries',
        default=False,
        help='Add the customer/vendor id into trial balance report.'
    )


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def _get_account_vals(self, company, account_template, code_acc, tax_template_ref):
        vals = super(AccountChartTemplate, self)._get_account_vals(company, account_template, code_acc,
                                                                   tax_template_ref)
        vals['with_auxiliaries'] = account_template.with_auxiliaries
        return vals
