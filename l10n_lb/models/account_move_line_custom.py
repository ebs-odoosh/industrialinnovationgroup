from odoo import fields, models, api, _


class ResConfigSettingCustom(models.Model):
    _inherit = "account.move.line"

    # foreign_debit = fields.Monetary(string='Debit', default=0.0, currency_field='currency_id')
    # foreign_credit = fields.Monetary(string='Credit', default=0.0, currency_field='currency_id')
    # foreign_balance = fields.Monetary(string='Balance', store=True,
    #                                   currency_field='currency_id',
    #                                   compute='_compute_foreign_balance')
    #
    # @api.depends('foreign_debit', 'foreign_credit')
    # def _compute_foreign_balance(self):
    #     for line in self:
    #         line.foreign_balance = line.foreign_debit - line.foreign_balance
    account_group_id = fields.Many2one(
        comodel_name='account.group',
        string="Account Group",
        related='account_id.group_id',
        store=True,
        readonly=True,
        required=False)



    price_subtotal_dollar = fields.Float(
        string='Price Subtotal Dollar',
        required=False, default=0.0)

    @api.model
    def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency, company, date):
        ''' This method is used to recompute the values of 'amount_currency', 'debit', 'credit' due to a change made
        in some business fields (affecting the 'price_subtotal' field).

        :param price_subtotal:  The untaxed amount.
        :param move_type:       The type of the move.
        :param currency:        The line's currency.
        :param company:         The move's company.
        :param date:            The move's date.
        :return:                A dictionary containing 'debit', 'credit', 'amount_currency'.
        '''
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1
        price_subtotal *= sign
        subtotal_dollar = 0
        result = {}

        if currency and currency != company.currency_id:
            # Multi-currencies.
            balance = currency._convert(price_subtotal, company.currency_id, company, date)
            if company.currency_id.id != 2:
                subtotal_dollar = company.currency_id._convert(price_subtotal, self.env['res.currency'].browse(2),
                                                               company, date)
            else:
                subtotal_dollar = balance
            result['price_subtotal_dollar'] = subtotal_dollar
            result['currency_id'] = currency.id
            result['amount_currency'] = price_subtotal
            result['debit'] = balance > 0.0 and balance or 0.0
            result['credit'] = balance < 0.0 and -balance or 0.0
            # return {
            #     'currency_id': currency.id,
            #     'amount_currency': price_subtotal,
            #     'debit': balance > 0.0 and balance or 0.0,
            #     'credit': balance < 0.0 and -balance or 0.0,
            # }
        else:
            # Single-currency.
            if company.currency_id.id != 2:
                subtotal_dollar = company.currency_id._convert(price_subtotal, self.env['res.currency'].browse(2),
                                                               company, date)
            else:
                subtotal_dollar = price_subtotal
            result['price_subtotal_dollar'] = subtotal_dollar
            result['amount_currency'] = 0.0
            result['debit'] = price_subtotal > 0.0 and price_subtotal or 0.0
            result['credit'] = price_subtotal < 0.0 and -price_subtotal or 0.0
            # return {
            #     'amount_currency': 0.0,
            #     'debit': price_subtotal > 0.0 and price_subtotal or 0.0,
            #     'credit': price_subtotal < 0.0 and -price_subtotal or 0.0,
            # }
        return result
