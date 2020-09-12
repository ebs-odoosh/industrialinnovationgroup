# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re


class VATReport(models.Model):
    # _name = 'account.vat.report'
    _inherit = "account.move"
    tax_closing = fields.Boolean(
        string='Is Tax Closing',
        required=False,
        default=False)
    from_date = fields.Date(
        string='From Date',
        required=False)

    to_date = fields.Date(
        string='To Date',
        required=False)

    is_foreign_exchange = fields.Boolean(
        string='Is Foreign Exchange',
        required=False,
        default=False)
    foreign_exchange_rate = fields.Float(
        string='Foreign Exchange Rate',
        required=False)

    @api.model
    def create(self, vals):
        if vals.get('tax_closing', False) or vals.get('is_foreign_exchange', False):
            entry_field = ""
            if vals.get('tax_closing', False):
                entry_field = "tax_closing"
            else:
                entry_field = "is_foreign_exchange"
            to_date = datetime.strptime(vals['to_date'], "%Y-%m-%d").date()
            from_date = datetime.strptime(vals['from_date'], "%Y-%m-%d").date()
            if to_date < from_date:
                raise UserError(_("From date must be less than to date"))
            if not self._check_vat_report_dates(from_date, entry_field):
                raise UserError(_("There is an entry with this period."))
        return super(VATReport, self).create(vals)

    def write(self, vals):
        for move in self:
            if move.tax_closing or move.is_foreign_exchange:
                entry_field = ""
                if move.tax_closing:
                    entry_field = "tax_closing"
                else:
                    entry_field = "is_foreign_exchange"
                if vals.get('from_date', False) or vals.get('to_date', False):
                    if len(move.line_ids) > 0:
                        raise UserError(_("Delete entries before changing period"))
                    from_date = move.from_date
                    to_date = move.to_date
                    if vals.get('from_date', False):
                        from_date = datetime.strptime(vals['from_date'], "%Y-%m-%d").date()
                    if vals.get('to_date', False):
                        to_date = datetime.strptime(vals['to_date'], "%Y-%m-%d").date()
                    if to_date < from_date:
                        raise UserError(_("From date must be less than to date"))
                    if not move._check_vat_report_dates(from_date, entry_field, rec_id=move.id):
                        raise UserError(_("There is an entry with this period."))
        return super(VATReport, self).write(vals)

    def _check_vat_report_dates(self, from_date, entry_field, rec_id=0):
        domain = [
            (entry_field, '=', True),
            ('state', '!=', 'cancel'),
            ('to_date', '>=', from_date)
        ]
        if rec_id != 0:
            domain.append(('id', '!=', rec_id))
        if len(self.env['account.move'].search(domain)) == 0:
            return True
        else:
            return False

    @api.depends('from_date', 'to_date')
    @api.onchange('from_date', 'to_date')
    def period_on_change(self):
        if self.name and self.name != '/':
            self.name = self.generate_name()

    def _check_balanced(self):
        return

    def generate_name(self):
        if self.tax_closing:
            return 'VAT Closing/' + str(self.to_date.year) + '/' + self.from_date.strftime(
                "%B") + '/' + self.to_date.strftime(
                "%B")
        if self.is_foreign_exchange:
            return 'Foreign Exchange/' + str(self.to_date.year) + '/' + self.from_date.strftime(
                "%B") + '/' + self.to_date.strftime(
                "%B")

    def _get_move_display_name(self, show_ref=False):
        self.ensure_one()
        if self.tax_closing or self.is_foreign_exchange:
            return self.generate_name()
        return super(VATReport, self)._get_move_display_name()

    def delete_entries(self):
        entries_list = self.env['account.move.line'].search([
            ('move_id', "=", self.id),
            ('parent_state', "=", "draft")
        ])
        for entry in entries_list:
            entry.unlink()

    def create_move_line(self, move_id, move_name, date, journal_id, company_id, company_currency_id,
                         account_id, account_internal_type, name, debit, credit, balance, reconciled):
        self.env['account.move.line'].create({
            "move_id": move_id,
            "move_name": move_name,
            "date": date,
            "parent_state": "draft",
            "journal_id": journal_id,
            "company_id": company_id,
            "company_currency_id": company_currency_id,
            "account_id": account_id,
            "account_internal_type": account_internal_type,
            "name": name,
            "quantity": 1.0,
            "discount": 0.0,
            "debit": debit,
            "credit": credit,
            "balance": balance,
            "reconciled": reconciled,
            "blocked": False,
            "tax_exigible": True,
            "amount_residual": 0.0,
            "amount_residual_currency": 0.0
        })

    def generate_vat_report(self):
        # self.env.cr.commit()
        entries_list = self.env['account.move.line'].search(
            [('move_id', "=", self.id)]
            , order='sequence asc')
        # closing_accounts = []
        closing_credit = 0.0
        closing_debit = 0.0
        if not self.from_date or not self.to_date:
            raise UserError("Fill all field")
        if len(entries_list) != 0:
            raise UserError("Entries already generated")
        report_config_list = self.env['account.vat.report.config'].search([], order="sequence")
        for report_config in report_config_list:
            if report_config.final_step:
                if closing_credit != 0.0 or closing_debit != 0.0:
                    acc_debit = 0.0
                    acc_credit = 0.0
                    diff = closing_debit - closing_credit
                    if diff > 0.0:
                        acc_credit = abs(diff)
                    else:
                        acc_debit = abs(diff)

                    create_move_line(self, self.id, self.name, self.date, self.journal_id.id,
                                     self.company_id.id, self.company_id.currency_id.id,
                                     report_config.account.id, report_config.account.internal_type,
                                     self.generate_name(), acc_debit, acc_credit,
                                     (acc_debit - acc_credit),
                                     True)

                else:
                    raise UserError(_("No entries available for this period."))

            else:
                accounts_list = self.env['account.account'].search([("group_id", "=", report_config.group.id)])
                global_debit = 0.0
                global_credit = 0.0
                for account in accounts_list:
                    debit = 0.0
                    credit = 0.0
                    line_list = self.env["account.move.line"].search([
                        ("account_id", "=", account.id),
                        ("company_id", "=", self.company_id.id),
                        # ("journal_id", "=", self.journal_id.id),
                        ("date", ">=", self.from_date),
                        ("date", "<=", self.to_date),
                        ("parent_state", "=", "posted")
                    ])
                    for line in line_list:
                        debit += line.debit
                        credit += line.credit
                    if debit != 0.0 or credit != 0.0:
                        self.create_move_line(self.id, self.name, self.date, self.journal_id.id,
                                              self.company_id.id, self.company_id.currency_id.id,
                                              report_config.account.id, report_config.account.internal_type,
                                              self.generate_name(), credit, debit,
                                              (credit - debit), True)

                    global_credit += credit
                    global_debit += debit

                closing_credit += global_debit
                closing_debit += global_credit
                if global_credit != 0.0 or global_debit != 0.0:
                    self.create_move_line(self.id, self.name, self.date, self.journal_id.id,
                                          self.company_id.id, self.company_id.currency_id.id,
                                          report_config.account.id, report_config.account.internal_type,
                                          self.generate_name(), global_debit, global_credit,
                                          (global_debit - global_credit), True)

                    self.create_move_line(self.id, self.name, self.date, self.journal_id.id,
                                          self.company_id.id, self.company_id.currency_id.id,
                                          report_config.account.id, report_config.account.internal_type,
                                          self.generate_name(), global_credit, global_debit,
                                          (global_credit - global_debit), True)

    def generate_foreign_exchange_report(self):
        config_list = self.env['account.foreign.exchange.report.config'].search([], order='date desc')
        if len(config_list) == 0:
            raise UserError(_("Missing Foreign Exchange Configuration."))
        config = config_list[0]
        accounts = []
        if len(config.group_ids) == 0:
            raise UserError(_("Missing Groups in Configuration"))

        account_obj = self.env['account.account']
        self.env.add_to_compute(account_obj._fields['root_id'], account_obj.search([]))

        for group in config.group_ids:
            accounts.extend(self.env['account.account'].search([('root_id', '=', ord(group.code_prefix[0]))]))

        for acc in accounts:
            entry_list = self.env["account.move.line"].search([
                ("account_id", "=", acc.id),
                ("company_id", "=", self.company_id.id),
                ("currency_id", "=", self.currency_id.id),
                ("date", ">=", self.from_date),
                ("date", "<=", self.to_date),
                ("parent_state", "=", "posted")])
            balance = 0.0
            balance_foreign = 0.0
            if len(entry_list) > 0:
                for entry in entry_list:
                    balance += entry.balance
                    balance_foreign += entry.amount_currency
                new_balance_foreign = abs(balance) * self.foreign_exchange_rate
                difference_foreign = abs(balance_foreign) - new_balance_foreign
                difference_current_cur = difference_foreign / self.foreign_exchange_rate
                if balance != 0.0:
                    if balance < 0.0:
                        if difference_foreign > 0.0:
                            self.create_move_line(self.id, self.name, self.date, self.journal_id.id,
                                                  self.company_id.id, self.company_id.currency_id.id,
                                                  acc.id, acc.internal_type, self.generate_name(),
                                                  abs(difference_current_cur), 0, difference_current_cur, True)

                            self.create_move_line(self.id, self.name, self.date, self.journal_id.id,
                                                  self.company_id.id, self.company_id.currency_id.id,
                                                  config.account_gain.id, config.account_gain.internal_type,
                                                  self.generate_name(),
                                                  0, abs(difference_current_cur), difference_current_cur, True)
                        else:
                            self.create_move_line(self.id, self.name, self.date, self.journal_id.id,
                                                  self.company_id.id, self.company_id.currency_id.id,
                                                  acc.id, acc.internal_type, self.generate_name(),
                                                  0, abs(difference_current_cur), difference_current_cur, True)
                            self.create_move_line(self.id, self.name, self.date, self.journal_id.id,
                                                  self.company_id.id, self.company_id.currency_id.id,
                                                  config.account_loss.id, config.account_loss.internal_type,
                                                  self.generate_name(),
                                                  abs(difference_current_cur), 0, difference_current_cur, True)
                    else:
                        if difference_foreign > 0.0:
                            self.create_move_line(self.id, self.name, self.date, self.journal_id.id,
                                                  self.company_id.id, self.company_id.currency_id.id,
                                                  acc.id, acc.internal_type, self.generate_name(),
                                                  0, abs(difference_current_cur), difference_current_cur, True)
                            self.create_move_line(self.id, self.name, self.date, self.journal_id.id,
                                                  self.company_id.id, self.company_id.currency_id.id,
                                                  config.account_loss.id, config.account_loss.internal_type,
                                                  self.generate_name(),
                                                  abs(difference_current_cur), 0, difference_current_cur, True)
                        else:
                            self.create_move_line(self.id, self.name, self.date, self.journal_id.id,
                                                  self.company_id.id, self.company_id.currency_id.id,
                                                  acc.id, acc.internal_type, self.generate_name(),
                                                  abs(difference_current_cur), 0, difference_current_cur, True)
                            self.create_move_line(self.id, self.name, self.date, self.journal_id.id,
                                                  self.company_id.id, self.company_id.currency_id.id,
                                                  config.account_gain.id, config.account_gain.internal_type,
                                                  self.generate_name(),
                                                  0, abs(difference_current_cur), difference_current_cur, True)

    def post(self):
        for move in self:
            if not move.line_ids.filtered(lambda line: not line.display_type):
                raise UserError(_('You need to add a line before posting.'))
            if move.auto_post and move.date > fields.Date.today():
                date_msg = move.date.strftime(self.env['res.lang']._lang_get(self.env.user.lang).date_format)
                raise UserError(_("This move is configured to be auto-posted on %s" % date_msg))

            if not move.partner_id:
                if move.is_sale_document():
                    raise UserError(
                        _("The field 'Customer' is required, please complete it to validate the Customer Invoice."))
                elif move.is_purchase_document():
                    raise UserError(
                        _("The field 'Vendor' is required, please complete it to validate the Vendor Bill."))

            if move.is_invoice(include_receipts=True) and float_compare(move.amount_total, 0.0,
                                                                        precision_rounding=move.currency_id.rounding) < 0:
                raise UserError(_(
                    "You cannot validate an invoice with a negative total amount. You should create a credit note instead. Use the action menu to transform it into a credit note or refund."))

            # Handle case when the invoice_date is not set. In that case, the invoice_date is set at today and then,
            # lines are recomputed accordingly.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if not move.invoice_date and move.is_invoice(include_receipts=True):
                move.invoice_date = fields.Date.context_today(self)
                move.with_context(check_move_validity=False)._onchange_invoice_date()

            # When the accounting date is prior to the tax lock date, move it automatically to the next available date.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if move.company_id.tax_lock_date and move.date <= move.company_id.tax_lock_date:
                move.date = move.company_id.tax_lock_date + timedelta(days=1)
                move.with_context(check_move_validity=False)._onchange_currency()

        # Create the analytic lines in batch is faster as it leads to less cache invalidation.
        self.mapped('line_ids').create_analytic_lines()
        for move in self:
            if move.auto_post and move.date > fields.Date.today():
                raise UserError(_("This move is configured to be auto-posted on {}".format(
                    move.date.strftime(self.env['res.lang']._lang_get(self.env.user.lang).date_format))))

            move.message_subscribe([p.id for p in [move.partner_id, move.commercial_partner_id] if
                                    p not in move.sudo().message_partner_ids])

            to_write = {'state': 'posted'}
            if move.tax_closing or move.is_foreign_exchange:
                to_write['name'] = move.generate_name()
            else:
                if move.name == '/':
                    # Get the journal's sequence.
                    sequence = move._get_sequence()
                    if not sequence:
                        raise UserError(_('Please define a sequence on your journal.'))

                    # Consume a new number.
                    to_write['name'] = sequence.next_by_id(sequence_date=move.date)

            move.write(to_write)

            # Compute 'ref' for 'out_invoice'.
            if move.type == 'out_invoice' and not move.invoice_payment_ref:
                to_write = {
                    'invoice_payment_ref': move._get_invoice_computed_reference(),
                    'line_ids': []
                }
                for line in move.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
                    to_write['line_ids'].append((1, line.id, {'name': to_write['invoice_payment_ref']}))
                move.write(to_write)

            if move == move.company_id.account_opening_move_id and not move.company_id.account_bank_reconciliation_start:
                # For opening moves, we set the reconciliation date threshold
                # to the move's date if it wasn't already set (we don't want
                # to have to reconcile all the older payments -made before
                # installing Accounting- with bank statements)
                move.company_id.account_bank_reconciliation_start = move.date

        for move in self:
            if not move.partner_id: continue
            if move.type.startswith('out_'):
                field = 'customer_rank'
            elif move.type.startswith('in_'):
                field = 'supplier_rank'
            else:
                continue
            try:
                with self.env.cr.savepoint():
                    self.env.cr.execute("SELECT " + field + " FROM res_partner WHERE ID=%s FOR UPDATE NOWAIT",
                                        (move.partner_id.id,))
                    self.env.cr.execute("UPDATE res_partner SET " + field + "=" + field + "+1 WHERE ID=%s",
                                        (move.partner_id.id,))
                    self.env.cache.remove(move.partner_id, move.partner_id._fields[field])
            except psycopg2.DatabaseError as e:
                if e.pgcode == '55P03':
                    _logger.debug('Another transaction already locked partner rows. Cannot update partner ranks.')
                    continue
                else:
                    raise e
