# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import re
import logging


from odoo import models, fields, api, _

_logger = logging.getLogger('smsclient')

class ServerAction(models.Model):
    """
    Possibility to specify the SMS Gateway when configure this server action
    """
    _inherit = 'ir.actions.server'

    sms_server = fields.Many2one('sms.smsclient', 'SMS Server',
                                 help='Select the SMS Gateway configuration to use with this action')

    def run(self):
        context = {} if not self._context else self._context

        act_ids = []
        for action in self:
            obj_pool = self.env.get(action.model_id.model)
            obj = obj_pool.browse(context['active_id'])
            cxt = {
                'context': context,
                'object': obj,
                'time': time,
            }
            expr = eval(str(action.condition), cxt)
            if not expr:
                continue
            if action.state == 'sms':
                _logger.info('Send SMS')
                sms_pool = self.env['sms.smsclient']
                mobile = str(action.mobile)
                to = None
                try:
                    cxt.update({'gateway': action.sms_server})
                    if mobile:
                        to = eval(action.mobile, cxt)
                    else:
                        _logger.error('Mobile number not specified !')

                    text = eval(action.sms, cxt)
                    #TODO: Fix it, this can't be working
#                    vals = {
#                        'gateway': action.sms_server.id,
#                        'mobile_to': to,
#                    }
#                    sms_id = sms_pool.create(cr, uid, vals, context=context)
#                    sms = sms_pool.browse(cr, uid, sms_id, context=context)
#                    if sms_pool._send_message(cr, uid, sms, context=context) == True:
#                        _logger.info('SMS successfully send to : %s' % (to))
#                    else:
#                        _logger.error('Failed to send SMS to : %s' % (to))
                except Exception, e:
                    _logger.error('Failed to send SMS : %s' % repr(e))
            else:
                act_ids.append(action.id)

        if act_ids:
            return super(ServerAction, self).run()
        return False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
