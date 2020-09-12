from odoo import fields, models, api, _


class AccountTax(models.Model):
    _inherit = "account.tax"

    res_partner = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
        required=False)

    is_withholding_tax = fields.Boolean(
        comodel_name='Withholding'
    )

    withholding_expense_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Withholding Expense Account',
    )


class AccountTaxTemplate(models.Model):
    _inherit = "account.tax.template"

    is_withholding_tax = fields.Boolean(
        comodel_name='Withholding'
    )

    withholding_expense_account_id = fields.Many2one(
        comodel_name='account.account.template',
        string='Withholding Expense Account',
    )

    def _get_tax_vals(self, company, tax_template_to_tax):
        vals = super(AccountTaxTemplate, self)._get_tax_vals(company, tax_template_to_tax)
        vals['is_withholding_tax'] = self.is_withholding_tax
        # if self.withholding_expense_account_id:
        #     vals['withholding_expense_account_id'] = self.withholding_expense_account_id.id
        return vals
