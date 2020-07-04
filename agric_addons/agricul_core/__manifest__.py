# -*- coding: utf-8 -*-
{
    'name': "Agriculture Core",

    'summary': """
    Precalcul, et tous les autres besoins specifiques
        """,

    'description': """
        Precalcul, et tous les autres besoins specifiques
    """,

    'author': "Webmania",
    'website': "webmania.ma",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'base',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'report',
        'product',
        'sale',
        'stock',
        'purchase',
        'project',
        'web',
        'agricul_base',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'data/paper_report_format.xml',
        'views/region_culture.xml',
        'views/actions_menu.xml',
        'views/project.xml',
        'reports/project_report.xml',
        'reports/purchase_order_report.xml',
        'reports/sale_order_report.xml',
        'reports/invoice_report.xml',
        'reports/report_delivery_document.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}