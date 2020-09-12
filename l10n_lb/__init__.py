# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) 2008 JAILLET Simon - CrysaLEAD - www.crysalead.fr

from . import models
from . import wizards
from odoo import api, SUPERUSER_ID
from odoo.addons.account.models.chart_template import preserve_existing_tags_on_taxes

def _preserve_tag_on_taxes(cr, registry):
    preserve_existing_tags_on_taxes(cr, registry, 'l10n_lb')
    env = api.Environment(cr, SUPERUSER_ID, {})
    accounts = env['account.account'].search([('code', 'in', ['5301','5121','999999'])])
    accounts.unlink()

    journal_id = env['account.journal'].search([('name', '=', 'Cash'),('type', '=', 'cash')],limit=1)
    if journal_id:
        account = env['account.account'].search([('code', '=', '53000001')],limit=1)
        journal_id.write({
            'default_debit_account_id': account.id,
            'default_credit_account_id': account.id
        })
