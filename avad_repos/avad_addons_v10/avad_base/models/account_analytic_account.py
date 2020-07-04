# -*- coding: utf-8 -*-

import time
import math
from datetime import datetime, timedelta
from dateutil.relativedelta import *

from django.utils.encoding import smart_str, smart_unicode

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountAnalytic(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def recurring_create_invoice(self, limit=None):

        #todo upadete lignes contract from project.SOs.SOLS[if reccurent invoice]
        for o in self:
            lines = [(2, l.id) for l in o.recurring_invoice_line_ids]
            for p in o.project_ids:
                for so in p.sale_order_ids:
                    for sol in so.order_line:
                        if sol.used_in_inv_rec:
                            lines.append((0,0,{
                                'product_id': sol.product_id,
                                'quantity': sol.product_uom_qty,
                                'price_unit': sol.price_unit,
                                'name': sol.name,
                                'uom_id': sol.product_uom.id,
                            }))
            #print("========")

            o.recurring_invoice_line_ids = lines
        invoices = super(AccountAnalytic, self).recurring_create_invoice(limit=limit)
        # set dates
        for inv in invoices:
            dt_s = fields.Datetime.from_string(inv.date_invoice)
            dt_e = dt_s + relativedelta(months=1)
            inv.date_start_project_n = inv.date_invoice
            inv.date_end_project_n = fields.Date.to_string(dt_e.date())
            print("==== CREATE RECURRR:",inv.date_start_project_n,inv.date_end_project_n)
        try:
            self.send_sms_ruccrent_invoice(invoices)
        except Exception as e:
            print("Error send message in recurring invoices")
        return invoices

    @api.model
    def send_sms_ruccrent_invoice(self, invoices):
        for o in invoices:
            pat = o.partner_id
            prj = o.our_project_id
            ref = o.our_project_id and o.our_project_id.name or ''
            date_inv = str(o.date_invoice or '*')
            med = prj.medecin_prescripteur_id
            civ_med = med and med.civilite or ''
            if civ_med:
                civ_med = 'Dr' if civ_med == 'doctor' else 'Pr'
            #typex = o.type_examen_id and o.type_examen_id.name or ' '
            message = u"Une facture reccurente a ete cree, \nDossier : " + ref + "\nPAT : " + (
                    pat and pat.name or '') + "\nMed : " + (
                              med and med.name or '') + u"\nDate : "+date_inv
            message = u'' + message.encode('utf-8')
            # message = smart_unicode(message)
            users_sms = self.env['res.users'].search([('recoi_sms_inv', '=', True)])
            active_part_ids = [p.partner_id.id for p in users_sms if p.partner_id]
            if message and active_part_ids:
                self.env['sms.smsclient'].send_sms_msg_to_partners(active_part_ids=active_part_ids, add_msg=message)
