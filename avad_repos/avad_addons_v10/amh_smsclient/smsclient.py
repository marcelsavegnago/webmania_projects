# -*- coding: utf-8 -*-

import time
import urllib
import requests, json
import re
import logging
import codecs
from django.utils.encoding import smart_str, smart_unicode

from odoo import addons
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    from SOAPpy import WSDL
except:
    _logger.warning("ERROR IMPORTING SOAPpy, if not installed, please install it:"
                    " e.g.: apt-get install python-soappy")


#######################
# Model SMS
#######################

class maritime_sms(models.Model):
    _name = 'maritime.sms'
    _description = 'sms'

    name = fields.Char('Nom du modèle', size=64, required=True)
    description = fields.Text('Description SMS', required=True)


class partner_sms_send(models.Model):
    _name = "partner.sms.send"

    def _default_get_mobile(self):
        context = {} if not self._context else self._context
        partner_pool = self.env['res.partner']
        active_ids = context.get('active_ids')
        res = {}
        i = 0
        for partner in partner_pool.browse(active_ids):
            i += 1
            res = partner.mobile
        if i > 1:
            raise ValidationError(_('You can only select one partner'))
        return res

    def _default_get_gateway(self):
        context = {} if not self._context else self._context
        sms_obj = self.env['sms.smsclient']
        gateway_ids = sms_obj.search([], limit=1)
        return gateway_ids and gateway_ids[0] or False

    @api.onchange("gateway")
    def onchange_gateway(self):
        context = {} if not self._context else self._context
        sms_obj = self.env['sms.smsclient']
        for o in self:
            if not o.gateway:
                return {}
            gateway = o.gateway
            return {
                'value': {
                    'validity': gateway.validity,
                    'classes': gateway.classes,
                    'deferred': gateway.deferred,
                    'priority': gateway.priority,
                    'coding': gateway.coding,
                    'tag': gateway.tag,
                    'nostop': gateway.nostop,
                }
            }

    @api.onchange("model_sms")
    def onchange_gateway_sms(self):
        context = self._context
        if context is None:
            context = {}
        for o in self:
            if not o.model_sms:
                return {}
            gateway = o.model_sms
            return {
                'value': {
                    'body': gateway.description,

                }
            }

    model_sms = fields.Many2one('maritime.sms', 'Model SMS')
    mobile_to = fields.Char('To', size=256, required=True, default=_default_get_mobile)
    app_id = fields.Char('API ID', size=256)
    login = fields.Char('Login', size=256)
    psw = fields.Char('Psw', size=256)
    body = fields.Text('Message', required=True,
                       help="The message text that will be send along with the email which is send through this server")
    gateway = fields.Many2one('sms.smsclient', 'SMS Gateway', required=True, default=_default_get_gateway)
    validity = fields.Integer('Validity',
                              help="the maximum time -in minute(s)- "
                                   "before the message is dropped")
    classes = fields.Selection([
        ('0', 'Flash'),
        ('1', 'Phone display'),
        ('2', 'SIM'),
        ('3', 'Toolkit')
    ], 'Class',
        help="The sms class: flash(0), "
             "phone display(1), SIM(2), toolkit(3)")
    deferred = fields.Integer('Deferred',
                              help="The time -in minute(s)- "
                                   "to wait before sending the message")
    priority = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3')
    ], 'Priority',
        help="The priority of the message")
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
    ], 'Coding',
        help="The SMS coding: 1 for 7 bit "
             "or 2 for unicode")
    tag = fields.Char('Tag', size=256, help='an optional tag')
    nostop = fields.Selection([
        ('0', '0'),
        ('1', '1')
    ], 'NoStop',
        help='Do not display STOP clause in the message, this requires that this is not an advertising message')

    def sms_send(self):
        context = {} if not self._context else self._context
        client_obj = self.env['sms.smsclient']
        for data in self:
            if not data.gateway:
                raise ValidationError(_('No Gateway Found'))
            else:
                client_obj._send_message(data)
        return {}


class lead_sms_send(models.Model):
    _name = "lead.sms.send"

    def _default_get_mobile(self):
        context = {} if not self._context else self._context
        partner_pool = self.env['project.project']
        active_ids = context.get('active_ids')
        res = {}
        i = 0
        for project in partner_pool.browse(active_ids):
            i += 1
            res = project.medecin_prescripteur_id and project.medecin_prescripteur_id.mobile
        if i > 1:
            raise ValidationError(_('You can only select one partner'))
        return res

    def _default_get_gateway(self):
        context = {} if not self._context else self._context
        sms_obj = self.env['sms.smsclient']
        gateway_ids = sms_obj.search([], limit=1)
        return gateway_ids and gateway_ids[0] or False

    @api.onchange("gateway")
    def onchange_gateway(self):
        context = {} if not self._context else self._context
        sms_obj = self.env['sms.smsclient']
        for o in self:
            if not o.gateway:
                return {}
            gateway = o.gateway
            return {
                'value': {
                    'validity': gateway.validity,
                    'classes': gateway.classes,
                    'deferred': gateway.deferred,
                    'priority': gateway.priority,
                    'coding': gateway.coding,
                    'tag': gateway.tag,
                    'nostop': gateway.nostop,
                }
            }

    @api.onchange("model_sms")
    def onchange_gateway_sms(self):
        context = self._context
        if context is None:
            context = {}
        for o in self:
            if not o.model_sms:
                return {}
            gateway = o.model_sms
            return {
                'value': {
                    'body': gateway.description,

                }
            }

    model_sms = fields.Many2one('maritime.sms', 'Model SMS')
    mobile_to = fields.Char('To', size=256, required=True, default=_default_get_mobile)
    app_id = fields.Char('API ID', size=256)
    login = fields.Char('Login', size=256)
    psw = fields.Char('Psw', size=256)
    body = fields.Text('Message', required=True,
                       help="The message text that will be send along with the email which is send through this server")
    gateway = fields.Many2one('sms.smsclient', 'SMS Gateway', required=True, default=_default_get_gateway)
    validity = fields.Integer('Validity',
                              help="the maximum time -in minute(s)- "
                                   "before the message is dropped")
    classes = fields.Selection([
        ('0', 'Flash'),
        ('1', 'Phone display'),
        ('2', 'SIM'),
        ('3', 'Toolkit')
    ], 'Class',
        help="The sms class: flash(0), "
             "phone display(1), SIM(2), toolkit(3)")
    deferred = fields.Integer('Deferred',
                              help="The time -in minute(s)- "
                                   "to wait before sending the message")
    priority = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3')
    ], 'Priority',
        help="The priority of the message")
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
    ], 'Coding',
        help="The SMS coding: 1 for 7 bit "
             "or 2 for unicode")
    tag = fields.Char('Tag', size=256, help='an optional tag')
    nostop = fields.Selection([
        ('0', '0'),
        ('1', '1')
    ], 'NoStop',
        help='Do not display STOP clause in the message, this requires that this is not an advertising message')

    def sms_send(self):
        context = {} if not self._context else self._context
        client_obj = self.env['sms.smsclient']
        for data in self:
            if not data.gateway:
                raise ValidationError(_('No Gateway Found'))
            else:
                client_obj._send_message(data)
        return {}


class SMSClient(models.Model):
    _name = 'sms.smsclient'
    _description = 'SMS Client'

    name = fields.Char('Gateway Name', size=256, required=True)
    url = fields.Char('Gateway URL', size=256, required=True, default="https://www.smsconnect.ma/sendsms/",
                      help='Base url for message')
    login = fields.Char('Login', size=256, required=True)
    psw = fields.Char('Psw', size=256, required=True)
    signature = fields.Char('Signature', size=256, required=True)
    mobile_to = fields.Char('To', size=256, required=True)
    body = fields.Text('Message',
                       help="The message text that will be send along with the email which is send through this server")
    history_line = fields.One2many("sms.smsclient.history", 'gateway_id', 'History')
    method = fields.Selection([
        ('http', 'HTTP Method'),
        ('smpp', 'SMPP Method')
    ], 'API Method', select=True, default='http')
    state = fields.Selection([
        ('new', 'Not Verified'),
        ('waiting', 'Waiting for Verification'),
        ('confirm', 'Verified'),
    ], 'Gateway Status', select=True, default='new')

    users_id = fields.Many2many("res.users", 'res_smsserver_group_rel', 'sid', 'uid', 'Users Allowed')
    code = fields.Char('Verification Code', size=256)
    body = fields.Text('Message', default='Test Sline',
                       help="The message text that will be send along with the email which is send through this server")
    validity = fields.Integer('Validity', default=10,
                              help='The maximum time -in minute(s)- before the message is dropped')
    classes = fields.Selection([
        ('0', 'Flash'),
        ('1', 'Phone display'),
        ('2', 'SIM'),
        ('3', 'Toolkit')
    ], 'Class', default='1', help='The SMS class: flash(0),phone display(1),SIM(2),toolkit(3)')
    deferred = fields.Integer('Deferred', default=0, help='The time -in minute(s)- to wait before sending the message')
    priority = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3')
    ], 'Priority', default='3', help='The priority of the message ')
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
    ], 'Coding', default='1', help='The SMS coding: 1 for 7 bit or 2 for unicode')
    tag = fields.Char('Tag', size=256, help='an optional tag')
    nostop = fields.Selection([
        ('0', '0'),
        ('1', '1')
    ], 'NoStop', default='1',
        help='Do not display STOP clause in the message, this requires that this is not an advertising message')

    @api.model
    def _check_permissions(self, uid, id):
        self.env.cr.execute("SELECT * FROM res_smsserver_group_rel "
                            "WHERE sid=%s AND uid=%s" % (id, uid))
        data = self.env.cr.fetchall()
        if len(data) <= 0:
            return False
        return True

    def _prepare_smsclient_queue(self, data, name):
        return {
            'name': name,
            'gateway_id': data.gateway.id,
            'state': 'draft',
            'mobile': data.mobile_to,
            'msg': smart_str(data.body),
            'validity': data.validity,
            'classes': data.classes,
            'deferred': data.deferred,
            'priority': data.priority,
            'coding': data.coding,
            'tag': data.tag,
            'nostop': data.nostop,
        }

    @api.model
    def _send_message(self, data):
        import urllib
        context = {} if not self._context else self._context
        gateway = data.gateway

        if gateway:
            if not self._check_permissions(self.env.user.id, gateway.id):
                raise ValidationError(_('You have no permission to access %s ') % (gateway.name,))
            url = gateway.url

            prms = {}
            config = {}
            config['login'] = gateway.login
            config['password'] = gateway.psw
            config['oadc'] = gateway.signature
            config['msisdn_to'] = data.mobile_to
            config['body'] = data.body
            params = urllib.urlencode(prms)
            name = url + "?" + params

            params = urllib.urlencode(config)
            f = urllib.urlopen(url + "?" + params)

            queue_obj = self.env['sms.smsclient.queue']
            vals = self._prepare_smsclient_queue(data, f)
            queue_obj.create(vals)

        return True

    def _check_queue(self):

        context = {} if not self._context else self._context
        queue_obj = self.env['sms.smsclient.queue']
        history_obj = self.env['sms.smsclient.history']
        sids = queue_obj.search([
            ('state', '!=', 'send'),
            ('state', '!=', 'sending')
        ], limit=30)
        sids.write({'state': 'sending'})
        error_ids = []
        sent_ids = []

        for sms in sids:
            if len(sms.msg) > 160:
                error_ids.append(sms.id)
                continue

            history_obj.create({
                'name': _('SMS Sent'),
                'gateway_id': sms.gateway_id.id,
                'sms': sms.msg,
                'to': sms.mobile,
            })
            sent_ids.append(sms.id)

        queue_obj.browse(sent_ids).write({'state': 'send'})
        queue_obj.browse(error_ids).write({
            'state': 'error',
            'error': 'Size of SMS should not be more then 160 char'
        })
        return True

    @api.model
    def send_sms_msg_to_partners(self, active_part_ids, add_msg=''):
        gateway = self.env['sms.smsclient'].search([])
        if active_part_ids:
            active_part_ids = self.env['res.partner'].browse(active_part_ids)
            active_part_ids = active_part_ids.filtered(lambda p: p.mobile)
            active_part_ids = [p.id for p in active_part_ids]
        gateway = gateway[0] if len(gateway) else False
        try:
            sms_prj = self.with_context(active_part_ids=active_part_ids).env["part.sms.lead"].create({
                    'gateway': gateway and gateway.id or False,
                    'body': smart_str(add_msg),
            })
            sms_prj.sms_mass_send()

        except Exception as e:
            print("Some SMS not sended ===", e)


class SMSQueue(models.Model):
    _name = 'sms.smsclient.queue'
    _description = 'SMS Queue'

    name = fields.Text('SMS Request', size=256,
                       required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    msg = fields.Text('SMS Text', size=256,
                      required=True, readonly=True,
                      states={'draft': [('readonly', False)]})
    mobile = fields.Char('Mobile No', size=256,
                         required=True, readonly=True,
                         states={'draft': [('readonly', False)]})
    gateway_id = fields.Many2one('sms.smsclient',
                                 'SMS Gateway', readonly=True,
                                 states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Queued'),
        ('sending', 'Waiting'),
        ('send', 'Sent'),
        ('error', 'Error'),
        ('cancel', 'Cancel'),
    ], 'Message Status', select=True, readonly=True,
        default='draft')
    error = fields.Text('Last Error', size=256,
                        readonly=True,
                        states={'draft': [('readonly', False)]})
    date_create = fields.Datetime('Date', readonly=True,
                                  default=fields.Datetime.now())
    validity = fields.Integer('Validity',
                              help="The maximum time -in minute(s)- "
                                   "before the message is dropped")
    classes = fields.Selection([
        ('0', 'Flash'),
        ('1', 'Phone display'),
        ('2', 'SIM'),
        ('3', 'Toolkit')
    ], 'Class',
        help="The sms class: flash(0), "
             "phone display(1), SIM(2), toolkit(3)")
    deferred = fields.Integer('Deferred',
                              help="The time -in minute(s)- to wait "
                                   "before sending the message")
    priority = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
    ], 'Priority',
        help='The priority of the message ')
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
    ], 'Coding',
        help="The sms coding: 1 for 7 bit "
             "or 2 for unicode")
    tag = fields.Char('Tag', size=256,
                      help='An optional tag')
    nostop = fields.Boolean('NoStop',
                            help="Do not display STOP clause in the message, "
                                 "this requires that this is not an "
                                 "advertising message")


class HistoryLine(models.Model):
    _name = 'sms.smsclient.history'
    _description = 'SMS Client History'

    name = fields.Char('Description', size=160, required=True, readonly=True)
    date_create = fields.Datetime('Date', readonly=True, default=fields.Datetime.now())
    user_id = fields.Many2one('res.users', 'Username',
                              readonly=True, select=True, default= lambda slf: slf.env.user.id)
    gateway_id = fields.Many2one('sms.smsclient', 'SMS Gateway',
                                 ondelete='set null', required=True)
    to = fields.Char('Mobile No', size=15, readonly=True)
    sms = fields.Text('SMS', size=160, readonly=True)


    @api.model
    def create(self,vals):
        context = {} if not self._context else self._context
        res = super(HistoryLine, self).create(vals)
        self.env.cr.commit()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
