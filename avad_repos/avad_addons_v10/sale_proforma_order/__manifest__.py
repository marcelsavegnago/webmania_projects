# -*- coding: utf-8 -*-
# © 2017 Jérôme Guerriat
# © 2017 Niboo SPRL (https://www.niboo.be/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale - Pro Forma from quotation',
    'category': 'Sale',
    'summary': 'Allow to create Pro Forma from an unconfirmed sale order',
    'website': 'www.webmania.ma',
    'version': '10.0.1.0.0',
    'description': """
- Allow to print a Pro Forma invoice based on an unconfirmed sale order
        """,
    'author': 'WEBMANIA SOUTIONS',
    'depends': [
        'sale',
    ],
    'data': [
        'reports/sale_order_report.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'application': False,
}
