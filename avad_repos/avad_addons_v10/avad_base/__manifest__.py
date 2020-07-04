# -*- coding: utf-8 -*-

{
    'name': 'Avad BASE',
    'version': '0.1',
    'summary': 'The base of avad project',
    'description': """
        Avad Base
    """,
    'category': 'base',
    'author': "Abdelmajid, Webamania",
    'website': 'http://www.webmania.ma',
    'images': [
    ],
    'depends': [
        'base',
        'project',
        'sale',
        'purchase',
        'account',
        'sales_team',
        #'fleet',
        'contract',
        'account_invoice_production_lot',
        #'amh_smsclient',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',

        'data/data.xml',
        'data/paper_report_format.xml',

        'report/ppc_report.xml',
        'report/vni_report.xml',
        'report/o2_report.xml',
        'report/sommeil_report.xml',

        'views/task_views_interventions.xml',
        'views/partner_views.xml',
        'views/users_views.xml',
        'views/project_views.xml',
        'views/project_kanbans.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/account_invoice_views.xml',
        'views/specific.xml',
        'views/wizard_views.xml',
        'views/sommeil.xml',
        'views/products.xml',

        'views/actions_menu.xml',

    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    # 'post_init_hook': '_auto_install_l10n',
}
