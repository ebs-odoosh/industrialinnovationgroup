# -*- coding: utf-8 -*-
{
    'name': "EBS - Payroll",

    'summary': """
        EBS modification for payroll""",

    'description': """
    EBS modification for payroll
    """,

    'author': "jaafar khansa",
    'website': "http://www.ever-bs.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list

    'version': '0.1',

    # any module necessary for this one to work correctly
    'category': 'Payroll Localization',
    'depends': ['hr_payroll', 'hr_contract_reports','hr','hr_holidays'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/additional_elements_types_views.xml',
        'views/additional_elements_view.xml',
        'views/transportation_rule_view.xml',
        'views/hr_contract_view_custom.xml',
        'views/hr_payslip_view_custom.xml',
        'views/payslip_line_view.xml',
        'views/hr_employee_view_custom.xml',
        'views/hr_payroll_structure_custom.xml',
        'views/hr_job_custom_view.xml',
        'views/hr_leave_type_view_custom.xml',
        'views/allowance_request_type_view.xml',
        'views/allowance_request_view.xml',
        'views/menus.xml',
    ]
}
