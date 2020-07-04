# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'RIM POS ',
    'version' : '0.1',
    'summary': 'The pos of rim project',
    'description': """
        Pos Base
    """,
    'category': 'CRM',
    'author': "Majid, Webmania",
    'website': 'http://www.webmania.ma',
    'images' : [
    ],
    'depends' : [
        'base',
        'pos_ticket',
    ],
    'data': [
    ],
    'demo': [
    ],
    'qweb': [
        'static/src/xml/pos_ticket_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    #'post_init_hook': '_auto_install_l10n',
}
