from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.addons.base_gengo.models.res_company import res_company


class ResPartnerCustom(models.Model):
    _inherit = "res.partner"
    is_customer = fields.Boolean(string="Is a customer")
    is_supplier = fields.Boolean(string="Is a vendor")
    sales_vat_account = fields.Many2one(
        comodel_name='account.account',
        string='Account VAT Sales',
        required=False)

    purchase_vat_account = fields.Many2one(
        comodel_name='account.account',
        string='Account VAT Purchase',
        required=False)

    purchase_asset_vat_account = fields.Many2one(
        comodel_name='account.account',
        string='Account VAT Asset',
        required=False)
    purchase_service_vat_account = fields.Many2one(
        comodel_name='account.account',
        string='Account VAT Service',
        required=False)
    purchase_charges_vat_account = fields.Many2one(
        comodel_name='account.account',
        string='Account VAT Charges',
        required=False)

    payable_purchase_account = fields.Many2one(
        comodel_name='account.account',
        string='Account Payable Purchase and Service',
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        required=False)

    payable_asset_account = fields.Many2one(
        comodel_name='account.account',
        string='Account Payable Asset',
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        required=False)

    payable_charges_account = fields.Many2one(
        comodel_name='account.account',
        string='Account Payable Charges',
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        required=False)

    is_vendor_service_purchase = fields.Boolean(
        string='Is Service and Purchase ',
        required=False)
    is_vendor_asset = fields.Boolean(
        string='Is Asset',
        required=False)
    is_vendor_charges = fields.Boolean(
        string='Is Charges',
        required=False)
    account_number = fields.Char(
        string='Account number',
        required=False)

    # _sql_constraints = [
    #     ('contact_account_number_unique', 'unique (account_number)',
    #      'Account Number must be unique !'),
    # ]
    static_accounts = ['1004', '1005', '1001', '1006']

    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
                                                     string="Account Receivable",
                                                     domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
                                                     help="This account will be used instead of the default one as the receivable account for the current partner",
                                                     required=False,
                                                     default=None)
    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
                                                  string="Account Payable",
                                                  domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
                                                  help="This account will be used instead of the default one as the payable account for the current partner",
                                                  required=False,
                                                  default=None)

    def create_partner_tax(self, amount_type, account, type_tax_use):
        tva = self.env.company.vat_amount_default
        name = self.name + " - " + account.code + "- TVA " + str(tva) + "%"
        description = str(tva) + "%"
        tax = self.env['account.tax'].create(
            {
                "name": name,
                "amount_type": amount_type,
                "type_tax_use": type_tax_use,
                "amount": tva,
                "res_partner": self.id,
                "description": description
            }
        )
        repartition_for_invoices = self.env['account.tax.repartition.line'].search([("invoice_tax_id", "=", tax.id),
                                                                                    ("repartition_type", "=", "tax")
                                                                                    ],
                                                                                   limit=1)
        repartition_for_crd_note = self.env['account.tax.repartition.line'].search([("refund_tax_id", "=", tax.id),
                                                                                    ("repartition_type", "=", "tax")
                                                                                    ],
                                                                                   limit=1)
        repartition_for_crd_note.account_id = account.id
        repartition_for_invoices.account_id = account.id
        return tax

    def create_partner_account(self):
        if not self.account_number:
            raise ValidationError(_("Partner account number is missing!"))
        if self.is_supplier:
            if self.is_vendor_service_purchase:
                if not self.payable_purchase_account:
                    payable_purchase_auto_gen = self.env['account.auto.generate.mapping'].search(
                        [('type', '=', 'app')],
                        limit=1)
                    payable_purchase_acct = self.create_account(
                        payable_purchase_auto_gen.related_account.id,
                        self.name, "Payable Service and Purchase",
                        payable_purchase_auto_gen.related_account.code_prefix,
                        self.account_number,
                        payable_purchase_auto_gen.account_type.id
                    )
                    self.payable_purchase_account = payable_purchase_acct.id
                    # self.property_account_payable_id = payable_purchase_acct.id
                    # self.auto_generate_map_seq_increment(payable_auto_gen)

                if not self.purchase_service_vat_account:
                    purchase_auto_gen = self.env['account.auto.generate.mapping'].search([('type', '=', 'vatp')],
                                                                                         limit=1)
                    purchase_acc = self.create_account(
                        purchase_auto_gen.related_account.id,
                        self.name, "VAT Purchase and Services",
                        purchase_auto_gen.related_account.code_prefix,
                        self.account_number,
                        purchase_auto_gen.account_type.id)
                    self.purchase_service_vat_account = purchase_acc.id
                    # self.auto_generate_map_seq_increment(purchase_auto_gen)
                    self.create_partner_tax("percent", purchase_acc, "purchase")
            if self.is_vendor_asset:
                if not self.payable_asset_account:
                    payable_asset_auto_gen = self.env['account.auto.generate.mapping'].search(
                        [('type', '=', 'apa')],
                        limit=1)
                    payable_asset_acct = self.create_account(
                        payable_asset_auto_gen.related_account.id,
                        self.name, "Payable Asset",
                        payable_asset_auto_gen.related_account.code_prefix, self.account_number,
                        payable_asset_auto_gen.account_type.id
                    )
                    self.payable_asset_account = payable_asset_acct.id

                if not self.purchase_asset_vat_account:
                    asset_auto_gen = self.env['account.auto.generate.mapping'].search([('type', '=', 'vata')],
                                                                                      limit=1)
                    asset_acc = self.create_account(
                        asset_auto_gen.related_account.id,
                        self.name, "VAT Asset",
                        asset_auto_gen.related_account.code_prefix, self.account_number,
                        asset_auto_gen.account_type.id)
                    self.purchase_asset_vat_account = asset_acc.id
                    # self.auto_generate_map_seq_increment(asset_auto_gen)
                    self.create_partner_tax("percent", asset_acc, "purchase")
            if self.is_vendor_charges:
                if not self.payable_charges_account:
                    payable_charge_auto_gen = self.env['account.auto.generate.mapping'].search(
                        [('type', '=', 'apc')],
                        limit=1)
                    payable_charge_acct = self.create_account(
                        payable_charge_auto_gen.related_account.id,
                        self.name, "Payable Charges",
                        payable_charge_auto_gen.related_account.code_prefix, self.account_number,
                        payable_charge_auto_gen.account_type.id
                    )
                    self.payable_charges_account = payable_charge_acct.id

                if not self.purchase_charges_vat_account:
                    charges_auto_gen = self.env['account.auto.generate.mapping'].search([('type', '=', 'vatc')],
                                                                                        limit=1)
                    charges_acc = self.create_account(
                        charges_auto_gen.related_account.id,
                        self.name, "VAT Charges",
                        charges_auto_gen.related_account.code_prefix, self.account_number,
                        charges_auto_gen.account_type.id)
                    self.purchase_charges_vat_account = charges_acc.id
                    # self.auto_generate_map_seq_increment(charges_auto_gen)
                    self.create_partner_tax("percent", charges_acc, "purchase")

        if self.is_customer:
            create_account_receivable = False
            if self.property_account_receivable_id:
                default_receivable_account_id = int(
                    self.env['ir.property'].search([('name', '=', 'property_account_receivable_id')])[
                        0].value_reference.split(',')[1])
                if self.property_account_receivable_id.id == default_receivable_account_id:
                    create_account_receivable = True
            else:
                create_account_receivable = True

            if create_account_receivable:
                receivalble_auto_gen = self.env['account.auto.generate.mapping'].search([('type', '=', 'ar')], limit=1)
                receivable_acct = self.create_account(
                    receivalble_auto_gen.related_account.id,
                    self.name, "Receivable Sales",
                    receivalble_auto_gen.related_account.code_prefix, self.account_number,
                    receivalble_auto_gen.account_type.id)

                self.property_account_receivable_id = receivable_acct.id
                # self.auto_generate_map_seq_increment(receivalble_auto_gen)
            if not self.sales_vat_account:
                sales_auto_gen = self.env['account.auto.generate.mapping'].search([('type', '=', 'vats')], limit=1)
                sales_acc = self.create_account(
                    sales_auto_gen.related_account.id,
                    self.name, "VAT Sales",
                    sales_auto_gen.related_account.code_prefix, self.account_number,
                    sales_auto_gen.account_type.id)
                self.sales_vat_account = sales_acc.id
                # self.auto_generate_map_seq_increment(sales_auto_gen)
                self.create_partner_tax("percent", sales_acc, "sale")
        self.env.cr.commit()

    @api.model
    def create(self, vals):
        if vals.get('account_number', False):
            if len(self.env['account.static.accounts.config'].search([('code', '=', vals.get('account_number'))])) == 0:
                if len(self.env['res.partner'].search([('account_number', '=', vals.get('account_number'))])) > 0:
                    raise ValidationError(_("There is already a partner with this account number."))
        res = super(ResPartnerCustom, self).create(vals)
        res.property_account_receivable_id = None
        res.property_account_payable_id = None
        return res

    def write(self, vals):
        if vals.get('account_number', False):
            if len(self.env['account.static.accounts.config'].search([('code', '=', vals.get('account_number'))])) == 0:
                if len(self.env['res.partner'].search(
                        [
                            ('account_number', '=', vals.get('account_number')),
                            ('id', '!=', self.id)
                        ])) > 0:
                    raise ValidationError(_("There is already a partner with this account number."))
        return super(ResPartnerCustom, self).write(vals)

    def auto_generate_map_seq_increment(self, auto_generate_object):
        cur_seq = int(auto_generate_object.next_number)
        cur_seq = cur_seq + 1
        auto_generate_object.write({"next_number": str(cur_seq)})
        # self.env.cr.commit()

    def create_account(self, group_id, name, name_prefix, code_prefix, code, type_id):
        name2 = False
        static_accounts_list = self.env['account.static.accounts.config'].search([('code', '=', code)])
        if len(static_accounts_list) > 0:
            acc_list = self.env['account.account'].search([('code', '=', (code_prefix + code))])
            if len(acc_list) != 0:
                return acc_list[0]
            else:
                name2 = static_accounts_list[0].name
        payable_account = self.env['account.account'].create(
            {
                "group_id": group_id,
                "name": name_prefix + " - " + (name2 or name),
                "code": code_prefix + code,
                "user_type_id": type_id,
                "reconcile": True
            }
        )
        # self.env.cr.commit()
        return payable_account
