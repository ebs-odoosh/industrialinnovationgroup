# -*- coding: utf-8 -*-
# License Odoo proprietary license V1.
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.

{
    'name': 'Lebanon - Accounting',
    'version': '2.0',
    'category': 'Localization',
    'description': """
This is the module to manage the accounting chart for Lebanon in Odoo.
========================================================================
""",
    'template': [
        'static/src/scss/account_searchpanel.scss'
    ],
    'depends': [
        'base',
        'account',
        'base_iban',
        'base_vat',
        'account_reports'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/l10n_lb_chart_data.xml',
        'data/account_groups.xml',
        # 'data/account_account_data.xml',
        # 'data/account_auto_generate_mapping_data.xml',
        # 'data/account_vat_report_config_data.xml',
        'data/account_chart_template_data.xml',
        'data/account_data.xml',
        'data/account_tax_data.xml',
        'views/views.xml',
        'wizards/create_partner_account_wiz_view.xml',
        'views/res_partner_custom_view.xml',
        'views/account_auto_generation_map_view.xml',
        'views/account_move_view_custom.xml',
        'views/foreign_exchange_report_config_view.xml',
        'views/vat_report_config_view.xml',
        'views/static_accounts_config_view.xml',
        'views/account_account_type_view.xml',
        'views/menus.xml'
    ],
    'post_init_hook': '_preserve_tag_on_taxes',
}
