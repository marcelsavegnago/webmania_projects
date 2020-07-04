# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Fasluca(<https://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Tasks attachement ',
    'version': '10.0.1.0.1',
    'summary': """Download Documents That are Attached to the tasks from Website""",
    'description': 'This Module allows customer to download documents '
                   'that are attached to the tasks from website',
    'category': 'portal',
    'author': 'Abdelmajid Elhamdaoui',
    'company': 'elhamdaouiabdelmajid',
    'website': "elhamdaouiabdelmajid@gmail.com",
    'depends': ['avad_base', 'website_project'],
    'data': [
        'views/template.xml'
    ],
    'images': [],
    'license': 'LGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
