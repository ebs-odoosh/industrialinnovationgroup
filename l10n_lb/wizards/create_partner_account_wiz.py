# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CreatePartnerAccounts(models.TransientModel):
    _name = 'ebs_mod.res.partner.create.account'
    _description = 'Create Account for Partners'
    partner_ids = fields.Many2many('res.partner', string='Partners')


    @api.model
    def default_get(self, fields):
        res = super(CreatePartnerAccounts, self).default_get(fields)
        res.update({'partner_ids': self._context.get('active_ids')})
        return res

    def create_accounts(self):
        for partner in self.partner_ids:
            if partner.account_number:
                partner.create_partner_account()

    # @api.depends('partner_ids')
    # def _compute_invalid_addresses(self):
    #     for wizard in self:
    #         invalid_partner_addresses = wizard.partner_ids.filtered(lambda p: not self.env['snailmail.letter']._is_valid_address(p))
    #         wizard.invalid_partner_ids = invalid_partner_addresses
    #         wizard.invalid_addresses = len(invalid_partner_addresses)


    # def invalid_addresses_action(self):
    #     return {
    #         'name': _('Invalid Addresses'),
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'kanban,tree,form',
    #         'res_model': 'res.partner',
    #         'domain': [('id', 'in', self.mapped('invalid_partner_ids').ids)],
    #     }
