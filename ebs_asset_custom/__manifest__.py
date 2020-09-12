# -*- coding: utf-8 -*-
{
    'name': "ebs_asset_custom",

    'summary': """
        Module to create asset from quotation view""",

    'description': """
        Module to create asset from quotation view
    """,

    'author': "ebs",
    'website': "http://www.ever-bs.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'purchase', 'account', 'account_asset', 'hr'],

    # always loaded
    'data': [
         'security/ir.model.access.csv',
        'wizards/create_asset_from_po_view.xml',
        'wizards/message_wiz_view.xml',
        'wizards/transfer_asset_view.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/asset_view_custom.xml',
        'views/asset_transfer_log.xml',
        'views/menu.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
