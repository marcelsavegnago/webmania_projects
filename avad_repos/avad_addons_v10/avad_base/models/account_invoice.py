# -*- coding: utf-8 -*-

import time
import math
from datetime import datetime
from django.utils.encoding import smart_str, smart_unicode

from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('origin', 'contract_id')
    def _get_project_sommeil(self):
        for o in self:
            o.our_project_id =False
            o.our_sommeil_id = False
            if o.origin and not o.contract_id:
                ords = self.env['sale.order'].search([('name','=', o.origin)])
                if len(ords):
                    if ords[0].our_project_id:
                        o.our_project_id = ords[0].our_project_id
                        o.agence_id = ords[0].our_project_id.agence_id
                    if ords[0].our_sommeil_id:
                        o.our_sommeil_id = ords[0].our_sommeil_id
                        o.agence_id = ords[0].our_sommeil_id.agence_id

            if o.contract_id:
                prjs = self.env['project.project'].search([('analytic_account_id', '=', o.contract_id.id)])
                if len(prjs):
                    o.our_project_id = prjs[0]
                    o.agence_id = prjs[0].agence_id


    @api.depends('our_project_id', 'our_sommeil_id')
    def get_medecins(self):
        for o in self:
            if o.our_project_id:
                o.partner_id = o.our_project_id.patient_id
                o.medecin_prescripteur_id = o.our_project_id.medecin_prescripteur_id
                o.medecin_traitant_id = o.our_project_id.medecin_traitant_id
                o.date_start_project_n = o.our_project_id.start_date_loc
                o.date_end_project_n = o.our_project_id.end_date_loc
            if o.our_sommeil_id:
                o.partner_id = o.our_sommeil_id.patient_id
                o.medecin_prescripteur_id = o.our_sommeil_id.medecin_prescripteur_id

                # o.medecin_traitant_id = o.our_sommeil_id.medecin_traitant_id

    # @api.onchange("our_project_id")
    # def onchnage_prj(self):
    #     for o in self:
    #         if o.our_project_id:
    #             o.date_start_project_n = o.our_project_id.start_date_loc
    #             o.date_end_project_n = o.our_project_id.end_date_loc

    @api.depends("date_invoice")
    def _compute_nb_jrs_create(self):
        for o in self:
            if o.date_invoice and o.contract_id:
                dt = fields.Date.from_string(o.date_invoice)
                o.nb_jours_create = (datetime.now().date() - dt).days

    medecin_prescripteur_id = fields.Many2one('res.partner', 'Medecin Prescripteur',
                                              domain=[('type_client', '=', 'medecins')], compute=get_medecins,
                                              store=True)
    medecin_traitant_id = fields.Many2one('res.partner', 'Medecin Traitant',
                                          domain=[('type_client', '=', 'medecins')], compute=get_medecins, store=True)
    our_project_id = fields.Many2one('project.project', string='Demande', compute=_get_project_sommeil, store=True)
    our_sommeil_id = fields.Many2one('pat.sommeil', string='Sommeil', compute=_get_project_sommeil, store=True)
    agence_id = fields.Many2one("crm.team", string="Agence", compute=_get_project_sommeil, store=True)
    specialite = fields.Many2one("avad.medcin.specialite", string="Spécialité", related='medecin_prescripteur_id.specialite')
    date_start_project_n = fields.Date(u"Date début")
    date_end_project_n = fields.Date(u"Date fin")
    nb_jours_create = fields.Integer("Nbr Jrs", compute=_compute_nb_jrs_create, help="for recurrent invoices", store=True)
    relance_ruc = fields.Selection([
        ('1', 'Relance 1'),
        ('2', 'Relance 2'),
        ('3', 'Relance 3'),
    ], string='Relance ruc')


    @api.model
    def temp_calcul_jrs_relance_ruc(self):
        invs = self.env['account.invoice'].search([
                    ('contract_id', '!=', False),
                    ('state', '!=', 'draft'),
                    ('relance_ruc', '!=', False),
                ])
        for inv in invs:
            inv.relance_ruc = False
        for relance in self.env['amh.relance.invoice'].search([]):
            if relance.nb_jours > 0:
                invs = self.env['account.invoice'].search([
                    ('contract_id', '!=', False),
                    ('state', '=', 'draft'),
                    ('nb_jours_create', '=', relance.nb_jours),
                ])
                for inv in invs:
                    inv.relance_ruc = relance.name

    @api.model
    def send_relance_ruc_sms(self):
        for relance in self.env['amh.relance.invoice'].search([]):
            if relance.nb_jours > 0:
                invs = self.env['account.invoice'].search([
                    ('contract_id', '!=', False),
                    ('state', '=', 'draft'),
                    ('nb_jours_create', '=', relance.nb_jours),
                ])
                invs.relance_ruc = relance.name
                for inv in invs:
                    msg = ''
                    active_part_ids = [u.partner_id.id for u in relance.users_ids if u.partner_id]
                    pat = inv.partner_id
                    pat_tel = pat.mobile or '-'
                    prj = inv.our_project_id
                    ref = inv.our_project_id and inv.our_project_id.name or ''
                    date_inv = str(inv.date_invoice or '*')
                    agence = inv.agence_id and inv.agence_id.name or ''
                    ech_date = inv.date_due or '-'
                    med = prj.medecin_prescripteur_id
                    civ_med = med and med.civilite or ''

                    if relance.name == '1':
                        msg = "Rappel 1: Veuillez verifier avec le patient le bon fonctionnement de l'appareillage."
                        msg += "\nAction: Appel telephonique"
                        msg += "\nPAT: "+(pat and pat.name)
                        msg += "\nAgence: "+agence
                        msg += "\nTel: "+pat_tel
                        msg += "\nMed: "+(med and med.name or '')
                    elif relance.name == '2':
                        msg = "Rappel 2: Veuillez informer le patient sur la date d'echeance du paiement."
                        msg += "\nPAT: " + (pat and pat.name)
                        msg += "\nAgence: " + agence
                        msg += "\nTel: " + pat_tel
                        msg += "\nMed: " + (med and med.name or '')
                        msg += "\nDate d'echeance: " + ech_date
                    elif relance.name == '3':
                        msg = "Rappel 3:  Attention !! une facture est impayee, veuillez appeler le patient et confirmer sa situation."
                        msg += "\nPAT: " + (pat and pat.name)
                        msg += "\nAgence: " + agence
                        msg += "\nTel: " + pat_tel
                        msg += "\nMed: " + (med and med.name or '')
                    if msg:
                        message = u'' + msg.encode('utf-8')
                        if message and active_part_ids:
                            self.env['sms.smsclient'].send_sms_msg_to_partners(active_part_ids=active_part_ids,
                                                                               add_msg=message)

    @api.model
    def send_relance_rucc_cron(self):
        rec = self.env['account.invoice'].search([
            ('contract_id', '!=', False),
            ('state', '=', 'draft'),
        ])
        rec._compute_nb_jrs_create()
        rec.send_relance_ruc_sms()

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        for o in res:
            if o.our_project_id:
                o.date_start_project_n = o.our_project_id.start_date_loc
                o.date_end_project_n = o.our_project_id.end_date_loc
        return res

    @api.multi
    def write(self, vals):
        if vals.get('state', 'draft') != 'draft':
            vals['relance_ruc'] = False
        res = super(AccountInvoice, self).write(vals)
        return res



class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def _compute_prod_lots(self):
        for line in self:
            if not line.order_line_ids:
                if line.invoice_id and line.invoice_id.contract_id:
                    if line.invoice_id and line.invoice_id.our_project_id:
                        sol_ids = []
                        for so in line.invoice_id.our_project_id.sale_order_ids:
                            for sol in so.order_line:
                                if sol.product_id.id == line.product_id.id:
                                    if sol_ids:
                                        sol_ids |= sol
                                    else:
                                        sol_ids = sol
                        print("==== SOL IDS", sol_ids)
                        if sol_ids:
                            sol = sol_ids.sorted(lambda r: r.id)[0]
                            print("SELECTED SOL ID", sol)
                            line.prod_lot_ids = sol.mapped("procurement_ids.move_ids.lot_ids")
                            print("LOTS IDS",line.prod_lot_ids)

            else:
                line.prod_lot_ids = self.mapped(
                'order_line_ids.procurement_ids.move_ids.lot_ids')
