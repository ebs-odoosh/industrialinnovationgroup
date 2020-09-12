# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    # def _auto_create_asset(self):
    #     create_list = []
    #     invoice_list = []
    #     auto_validate = []
    #     for move in self:
    #         if not move.is_invoice():
    #             continue
    #
    #         for move_line in move.line_ids:
    #             if move_line.account_id and (
    #                     move_line.account_id.can_create_asset) and move_line.account_id.create_asset != 'no' and not move.reversed_entry_id:
    #                 if not move_line.name:
    #                     raise UserError(
    #                         _('Journal Items of {account} should have a label in order to generate an asset').format(
    #                             account=move_line.account_id.display_name))
    #                 # for x in range(int(move_line.quantity)):
    #                 vals = {
    #                     'name': move_line.name,
    #                     'company_id': move_line.company_id.id,
    #                     'currency_id': move_line.company_currency_id.id,
    #                     'product_id': move_line.product_id.id,
    #                     'original_move_line_ids': [(6, False, move_line.ids)],
    #                     'state': 'draft',
    #                 }
    #                 model_id = move_line.account_id.asset_model
    #                 if model_id:
    #                     vals.update({
    #                         'model_id': model_id.id,
    #                     })
    #                 auto_validate.append(move_line.account_id.create_asset == 'validate')
    #                 invoice_list.append(move)
    #                 create_list.append(vals)
    #
    #     assets = self.env['account.asset'].create(create_list)
    #     for asset, vals, invoice, validate in zip(assets, create_list, invoice_list, auto_validate):
    #         if 'model_id' in vals:
    #             asset._onchange_model_id()
    #             asset._onchange_method_period()
    #             if validate:
    #                 asset.validate()
    #         if invoice:
    #             asset_name = {
    #                 'purchase': _('Asset'),
    #                 'sale': _('Deferred revenue'),
    #                 'expense': _('Deferred expense'),
    #             }[asset.asset_type]
    #             msg = _('%s created from invoice') % (asset_name)
    #             msg += ': <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>' % (invoice.id, invoice.name)
    #             asset.message_post(body=msg)
    #     return assets
