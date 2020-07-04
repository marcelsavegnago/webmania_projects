# -*- coding: utf-8 -*-

import time
import math
from datetime import datetime, timedelta
from django.utils.encoding import smart_str, smart_unicode

from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class TypeExam(models.Model):
    _name = "pat.type.examen"

    name = fields.Char(string="Nom", required=True)
    active = fields.Boolean("Active", default=True)


class SomeilPieceJointe(models.Model):
    _name = "sommeil.piece.jointe"
    _description = "Piece jointe"
    _order = 'name'

    name = fields.Char('Piece jointe', size=100, required=True)


class SommeilFormRapport(models.Model):
    _name = "sommeil.forme.rapport"
    _description = "Forme d'envoi"
    _order = 'name'

    name = fields.Char("Forme d'envoi", size=100, required=True)


class PatCanal(models.Model):
    _name = "pat.canal"
    _description = "Canal"
    _order = 'name'

    name = fields.Char(string="Nom", required=True)
    active = fields.Boolean("Active", default=True)


class PatSommeil(models.Model):
    """ pat sommeil """
    _name = "pat.sommeil"
    _description = "Acceuil"
    _order = "id desc"
    _inherit = ['mail.thread']

    def _compute_sale_order(self):
        for o in self:
            o.sale_orders_count = len(o.sale_order_ids)

    def _default_get_gateway(self):
        context = self._context or {}
        sms_obj = self.env['sms.smsclient']
        gateway_ids = sms_obj.search([], limit=1)
        return gateway_ids and gateway_ids[0] or False

    @api.depends('rdv_ids','rdv_ids.date','state')
    def _get_date(self):

        for history in self:
            a = False
            for record in history.rdv_ids:
                history.daterdv = record.date


    def _get_number_of_days(self):

        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

        for rec in self:
            from_dt = datetime.datetime.strptime(rec.date_intervention_desappareillage, DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(datetime.datetime.now(), DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        return diff_day

    daterdv = fields.Date(compute=_get_date, store=True, string="Date RDV")

    etat_appariel = fields.Selection((('bon', 'Bon'), ('mauvais', 'Mauvais')), 'Etat Appareil')

    # stock_line = fields.One2many('sommeil.stock', 'sommeil_id', 'Appareil/consommables')

    # nsr = fields.related('stock_line', 'nsr', type='char', string='N° série', store=False, readonly=True)

    rdv_ids = fields.One2many('sommeil.rdv', 'sommeil_id', 'RDV')

    name = fields.Char('Ref', size=522)

    agence_id = fields.Many2one('crm.team', 'Agence', required=True)

    channel_id = fields.Many2one('pat.canal', 'Canal', required=True)

    type_examen_id = fields.Many2one('pat.type.examen', 'Type Examen')

    vehicle_id = fields.Many2one('fleet.vehicle', 'Véhicule')

    motif_maint = fields.Text('Motif')

    date_creation = fields.Date('Reçue le', default=fields.Date.context_today)

    patient_id = fields.Many2one('res.partner', 'Patient',
                                 domain=[('type_client', '=', 'patient')])

    medecin_prescripteur_id = fields.Many2one('res.partner', 'Medecin Prescripteur',
                                              domain=[('type_client', '=', 'medecins')])
    specialite_med = fields.Many2one("avad.medcin.specialite", "Spécialité médecin",
                                     related='medecin_prescripteur_id.specialite')

    phone = fields.Char('Téléphone', size=64)
    fax = fields.Char('Fax', size=64)
    mobile = fields.Char('GSM', size=64)
    street = fields.Char('Adresse', size=128)

    state = fields.Selection((('open', 'Ouvert'), ('encours', 'En cours'), ('programme', 'Appareillage'),
                              ('desappareillage', 'Désappareillage'), ('termine', 'Terminé'),
                              ('facture', 'Facturé'), ('annule', 'Annulé'), ('incident', 'Incident')), 'Etat',
                             default='open')

    responsable_id = fields.Many2one('res.users', 'Responsable')

    description = fields.Text('Consignes.')

    adrress = fields.Text('Adresse Complete')

    date_intervention = fields.Datetime('Date et heure Appareillage', )
    duree = fields.Float('Durée Appareillage')
    duree_appareillage_app = fields.Float('Durée Déplacement Appareillage')
    intervenant_ids = fields.Many2many('res.users', 'sommeil_intervenant', 'sommeil_id', 'intervenant_id',
                                       'Intervenants Appareillage', )

    date_intervention_desappareillage = fields.Datetime('Date et heure Désappareillage', )
    duree_desappareillage = fields.Float('Durée Désappareillage')
    duree_desappareillage_depla = fields.Float('Durée Déplacement Désappareillage')
    intervenant_ids_desappareillage = fields.Many2many('res.users', 'sommeil_intervenant_desappareillage',
                                                       'sommeil_id2', 'intervenant_id2',
                                                       'Intervenants Désappareillage', )
    vehicle_id_desappareillage = fields.Many2one('fleet.vehicle', 'Véhicule')
    etat_appariel_desappareillage = fields.Selection((('bon', 'Bon'), ('mauvais', 'Mauvais')), 'Etat Appareil')

    delai_max = fields.Integer('Délai pour envoi du rapport(J)', default=2)

    color = fields.Integer('Color Index')

    stock = fields.Integer('Stock?')

    priority = fields.Selection([('1', 'Urgent'), ('2', 'Moyen Urgent'), ('3', 'Peu Urgent'), ('4', 'pas urgent')],
                                "Degré d'urgence", select=True, default='2')

    date_start = fields.Date('Début de location')

    date_end = fields.Date('Fin de location')

    active = fields.Boolean('Active', default=True)

    state2 = fields.Selection((('pod', 'Préparation outils de diagnostic'), ('intervention', 'Intervention'),
                               ('rapport', 'Rapport'), ('annule', 'Annulé')), 'Etat', default='pod')

    part_medecin = fields.Float('Dossier Administratif Medecin', digits=(20, 3))
    avance_medecin = fields.Float('Avance Medecin', digits=(20, 3))
    part_avad = fields.Float('Part Avad', digits=(20, 3))
    avance_avad = fields.Float('Avance Avad', digits=(20, 3))
    montant_total = fields.Float('Montant Total', digits=(20, 3))

    facture = fields.Selection((('facture_avad', 'AVAD'), ('facture_medecin', 'Médecin'), ('autre', 'Les Deux')),
                               'Etablissement de facture')

    mode_paiement = fields.Selection(
        (('espece', 'Espéce'), ('cheque', 'Chéque'), ('visa', 'Visa'), ('chequeespece', 'Chéque et Espéce')),
        'Mode de  Règlements')

    montant_facturer = fields.Float('Montant à facturer', digits=(20, 3))

    remarques_facturation = fields.Text('Remarques')

    date_rapport_enregistrement = fields.Date('Date de scorage')
    date_rapport_envoi = fields.Date('Date d\'envoi')
    date_rapport_reception = fields.Date('Date d\'accusé de réception')

    enregistrement_id = fields.Many2one('res.users', 'Scorage')

    envoi_id = fields.Many2one('res.users', 'Remis à')

    recu_par = fields.Text('Reçu Par')

    piece_jointe_ids = fields.Many2many('sommeil.piece.jointe', 'sommeil_piecejointe_rel2', 'sommeil_id',
                                        'piecejointe_id', 'Piéces jointes', )
    forme_envoi_ids = fields.Many2many('sommeil.forme.rapport', 'sommeil_forme_envoi_rel2', 'sommeil_id',
                                       'forme_envoi_id', 'Formes d\'envoi', )

    iah = fields.Float('IAH', digits=(20, 3))
    idx_desat = fields.Float('INDEX DE DESATURATION', digits=(20, 3))
    indx_mev = fields.Float('INDEX DE MICRO-EVEIL', digits=(20, 3))
    imc = fields.Float('IMC', digits=(20, 3))
    age = fields.Float('AGE', digits=(20, 3))

    iah_dorsale = fields.Float('IAH DORSALE', digits=(20, 3))
    roncho = fields.Selection((('oui', 'Oui'), ('Non', 'Non'),('jsp','Je ne sais pas')), 'RONCHOPATHIE')
    scor_epw = fields.Float('ECHELLE EPWORTH ', digits=(20, 3))
    duree_passe_90_satur = fields.Float('Durée passée sous 90% saturations', digits=(20, 3))
    conclu_suiv_someil = fields.Selection([
        ('1', 'SAHOS S\xc3\xa9v\xc3\xa8re'),
        ('2', 'SAHOS Mod\xc3\xa9r\xc3\xa9'),
        ('3', 'SAHOS L\xc3\xa9ger'),
        ('4', 'Pas de SAHOS'),
        ('5', 'SAHOS positionnel S\xc3\xa9v\xc3\xa8re (Position dorsale)'),
        ('6', 'SAHOS positionnel Mod\xc3\xa9r\xc3\xa9 (Position dorsale)'),
        ('7', 'SAHOS positionnel L\xc3\xa9ger (Position dorsale)'),
        ('8', 'SAHOCS S\xc3\xa9v\xc3\xa8re'),
        ('9', 'SAHOCS Mod\xc3\xa9r\xc3\xa9'),
        ('10', 'SAHOCS L\xc3\xa9ger'),

    ], 'Conclusion')
    ""

    hta = fields.Selection((('oui', 'Oui'), ('Non', 'Non'),('jsp','Je ne sais pas')), 'HTA')
    diabete = fields.Selection((('oui', 'Oui'), ('Non', 'Non'),('jsp','Je ne sais pas')), 'DIABETE')
    insomnie = fields.Selection((('oui', 'Oui'), ('Non', 'Non'),('jsp','Je ne sais pas')), 'INSOMNIE')
    sjsr = fields.Selection((('oui', 'Oui'), ('Non', 'Non'),('jsp','Je ne sais pas')), 'SJSR')

    gateway = fields.Many2one('sms.smsclient', 'SMS Gateway', default=_default_get_gateway)

    invoice_id = fields.Many2one('account.invoice', 'Invoice')
    sale_order_ids = fields.One2many('sale.order', 'our_sommeil_id', 'Devis/Bon commandes')
    sale_orders_count = fields.Integer('Bon commandes', default=0, compute=_compute_sale_order)

    motif = fields.Char("Motif d'annulation")
    sms_send = fields.Boolean("Sms send", default=False)

    def update_invoice(self, prestation, journal_id, invoice_id):
        self.write({'state': 'facture', 'invoice_id': invoice_id or False})

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('pat.sommeil') or '/'
        order = super(PatSommeil, self).create(vals)
        try:
            order.send_sms_sommeil()
        except Exception as e:
            print("ERROR: SEND SMS IN CREATE SOMMEIL:", e)
        return order

    def demmarer(self):
        for o in self:
            o.write({'state': 'encours'})

    def annulation_sommeil(self, motif):
        self.write({'motif': motif, 'state': 'annule'})

    def action_encours(self):
        self.write({'state': 'encours'})

    def action_appareiller(self):
        """ Changes the state to Exception.
        @return: True
        """
        self.write({'state': 'programme', 'state2': 'intervention'})
        return True

    def action_desappareillage(self):
        """ Changes the state to Exception.
        @return: True
        """
        self.write({'state': 'desappareillage'})
        return True

    def action_termine(self):
        """ Changes the state to Exception.
        @return: True
        """
        self.write({'state': 'termine', 'state2': 'rapport'})
        return True

    @api.onchange('patient_id')
    def onchange_medecin_prescripteur_id(self):
        if self.patient_id:
            patient = self.patient_id
            result = {
                'value': {
                    # 'medecin_prescripteur_id': medecin_prescripteur_id,
                    'phone': patient.phone,
                    'fax': patient.fax,
                    'mobile': patient.mobile,
                    'street': patient.street,
                }
            }
            return result

    def send_sms_sommeil(self):
        for o in self:
            ref = o.name or ''
            pat = o.patient_id
            med = o.medecin_prescripteur_id
            civ_med = med and med.civilite or ''
            if civ_med:
                civ_med = 'Dr' if civ_med == 'doctor' else 'Pr'
            typex = o.type_examen_id and o.type_examen_id.name or ' '
            message = u"Cher(e) "+(civ_med or '')+"\nVotre demande\nRef : " + ref + "\nPAT : " + (
                    pat and pat.name or '') + "\nMed : " + (
                              med and med.name or '') + u"\nType examen: " + typex + "\na ete prise en compte."
            message = u'' + message.encode('utf-8')
            # message = smart_unicode(message)
            users_sms = self.env['res.users'].search([('recoi_sms_som', '=', True)])
            active_part_ids = [p.partner_id.id for p in users_sms if p.partner_id]
            if o.responsable_id:
                if o.responsable_id.partner_id:
                    active_part_ids += [o.responsable_id.partner_id.id]
            active_part_ids = list(set(active_part_ids))
            pat_med = []
            if med:
                pat_med += [med.id]
            active_part_ids += pat_med
            if message and active_part_ids:
                self.env['sms.smsclient'].send_sms_msg_to_partners(active_part_ids=active_part_ids, add_msg=message)

    def send_sms_synthese(self):
        for o in self:
            ref = o.name or ''
            pat = o.patient_id
            med = o.medecin_prescripteur_id
            civ_med = med and med.civilite or ''
            if civ_med:
                civ_med = 'Dr' if civ_med == 'doctor' else 'Pr'
            typex = o.type_examen_id and o.type_examen_id.name or ' '
            message = u"Cher(e) "+(civ_med or '')+"\nVotre demande\nRef : " + ref + "\nPAT : " + (
                    pat and pat.name or '') + "\nMed : " + (
                              med and med.name or '') + u"\nType examen: " + typex + "\na ete prise en compte."
            message = u'' + message.encode('utf-8')
            # message = smart_unicode(message)
            users_sms = self.env['res.users'].search([('recoi_sms_som', '=', True)])
            active_part_ids = [p.partner_id.id for p in users_sms if p.partner_id]
            if o.responsable_id:
                if o.responsable_id.partner_id:
                    active_part_ids += [o.responsable_id.partner_id.id]
            active_part_ids = list(set(active_part_ids))
            pat_med = []
            if med:
                pat_med += [med.id]
            active_part_ids += pat_med
            if message and active_part_ids:
                self.env['sms.smsclient'].send_sms_msg_to_partners(active_part_ids=active_part_ids, add_msg=message)
                o.sms_send = True



class SommeilRdv(models.Model):
    _name = "sommeil.rdv"
    _description = "RDV"

    def _complete_name(self):
        for m in self:
            m.name = '**' if m.state2 == "tremotive" else ' '

    def _complete_name2(self):
        for m in self:
            m.name2 = str(m.seq_rdv or '') + '/' + str(m.nb_rdv or '')

    def _amount_all(self):
        for hbl in self:
            nb_rdv = 0
            seq_rdv = 0
            recherche = 0
            i = len(hbl.rdv_ids)
            j = 1
            k = 0
            for line2 in hbl.rdv_ids:
                if hbl.id == line2.id:
                    k = j
                else:
                    j = j + 1

            nb_rdv = i
            seq_rdv = k

            if nb_rdv == seq_rdv:
                recherche = 1
            hbl.recherche = recherche
            hbl.nb_rdv = nb_rdv
            hbl.seq_rdv = seq_rdv

    name = fields.Char(compute=_complete_name, string=" Reference", size=250)
    name2 = fields.Char(compute=_complete_name2, string=" Seq", size=250)
    nb_rdv = fields.Integer(compute=_amount_all, string='Nb RDV', multi='sums')
    seq_rdv = fields.Integer(compute=_amount_all, string='Seq RDV', multi='sums')
    recherche = fields.Integer(compute=_amount_all, string='recherche', multi='sums')
    date = fields.Datetime('Date', required=False)
    motif = fields.Text('Raison')
    sommeil_id = fields.Many2one('pat.sommeil', 'Origine')
    planning_id = fields.Many2one('sommeil.planning2', 'Planning')
    phone = fields.Char(related='sommeil_id.phone', readonly=True, size=128, string='Phone')
    rdv_ids = fields.One2many("sommeil.rdv", related="sommeil_id.rdv_ids", string="Rdvs")
    patient_id = fields.Many2one('res.partner', related='sommeil_id.patient_id', readonly=True,
                                 string='Patient')
    medecin_prescripteur_id = fields.Many2one('res.partner', related='sommeil_id.medecin_prescripteur_id',
                                              readonly=True, string='Medecin')
    agence_id = fields.Many2one('crm.team', related='sommeil_id.agence_id', readonly=True,
                                string='Agence')
    type_examen_id = fields.Many2one('pat.type.examen', related='sommeil_id.type_examen_id',
                                     readonly=True, string='Type Examen')
    demandeur = fields.Selection((('avad', 'AVAD'), ('patient', 'Patient')), 'Demandeur', default='patient')
    state = fields.Selection((('valide', 'Validé'), ('incident', 'Incident'), ('annule', 'Annulé')), 'State',
                             default=False)
    state2 = fields.Selection((('motive', 'Motivé'), ('tremotive', 'Très motivé')), 'Graduation')
    user_id = fields.Many2one('res.users', 'Utilisateur')

    @api.model
    def create(self, vals):
        res = super(SommeilRdv, self.with_context(ignore_sms=True)).create(vals)
        for o in res:
            if o.sommeil_id and o.sommeil_id.state == 'open' and o.state == 'valide':
                o.sommeil_id.demmarer()
            try:
                o.send_sms_sommeil_prise_rendezvous()
            except Exception as e:
                print("Erreur envoi SMS RDV sommeil:", e)
        return res

    @api.multi
    def write(self, vals):
        res = super(SommeilRdv, self).write(vals)
        for o in self:
            if o.sommeil_id and o.sommeil_id.state == 'open' and o.state == 'valide':
                o.sommeil_id.demmarer()
        try:
            if not self._context.get('ignore_sms', False):
                self.send_sms_sommeil_prise_rendezvous()
        except Exception as e:
            print("Erreur envoi SMS RDV sommeil:", e)
        return res

    def send_sms_sommeil_prise_rendezvous(self):
        for rdv in self:
            o = rdv.sommeil_id
            if rdv.state in ['valide', 'annule','incident'] and o:
                pat = o.patient_id
                med = o.medecin_prescripteur_id
                civ_med = med and med.civilite or ''
                if civ_med:
                    civ_med = 'Dr' if civ_med == 'doctor' else 'Pr'

                # message = smart_unicode(message)
                users_sms = self.env['res.users'].search([('recoi_sms_som', '=', True)])
                active_part_ids = [p.partner_id.id for p in users_sms if p.partner_id]
                if o.responsable_id:
                    if o.responsable_id.partner_id:
                        active_part_ids += [o.responsable_id.partner_id.id]
                active_part_ids = list(set(active_part_ids))
                pat_med = []
                if med:
                    pat_med += [med.id]
                active_part_ids += pat_med

                date_r = ' '
                if rdv.date:
                    date_r = str(fields.Datetime.from_string(rdv.date).date())
                message = ''
                if rdv.state == 'valide':
                    message = u"Confirmation de RDV:\nPat: " + (
                            pat and pat.name or '') + u"\nMed: " +(civ_med or '')+' '+ (
                                      med and med.name or '') + u"\nType examen: " + (
                                      o.type_examen_id and o.type_examen_id.name or '') + u"\nDate " + date_r + u" dans la soiree."
                elif rdv.state == 'annule':
                    message = u"Annulation de RDV:\nPat: " + (
                            pat and pat.name or '') + u"\nMed: " +(civ_med or '')+' '+ (
                                      med and med.name or '') + u"\nType examen: " + (
                                      o.type_examen_id and o.type_examen_id.name or '') \
                              + u"\nMotif : " + (rdv.motif or '') \
                              + u"\nDate " + date_r

                elif rdv.state == 'incident':
                    message = u"Incident changement RDV:\n"\
                                + u"PAT: "+ (pat and pat.name or '')+"\n"\
                                + u"Med: "+(civ_med or '')+' '+(med and med.name or '')+"\n"\
                                + u"Type examen: "+(o.type_examen_id and o.type_examen_id.name or '')+"\n"\
                                + u"Motif : "+ (rdv.motif or '')+"\n"\
                                + u"Nouveau RDV: "+(date_r or '')

                if message and active_part_ids:
                    message = u'' + message.encode('utf-8')
                    self.env['sms.smsclient'].send_sms_msg_to_partners(active_part_ids=active_part_ids, add_msg=message)


class SommeilPlanning2(models.Model):
    _name = "sommeil.planning2"
    _description = "planning"
    _order = 'name'

    def _ref_get_k(self):
        self.env.cr.execute('select max(ref) from sommeil_planning2', )
        resq = self.env.cr.fetchall()
        if resq[0][0] > 0:
            return 'SP/' + time.strftime("%Y") + '/' + str(int(resq[0][0]) + 1)
        return 'SP/' + time.strftime("%Y") + '/1'

    def _ref_get(self):
        self.env.cr.execute('select max(ref) from sommeil_planning2', )
        resq = self.env.cr.fetchall()
        print resq
        if resq[0][0] > 0:
            return int(resq[0][0]) + 1
        return 1

    name = fields.Char('Nom', size=100, readonly=True, default=_ref_get_k)
    ref = fields.Integer('Réf', size=100, readonly=True, default=_ref_get)
    date = fields.Date('Date de planing', readonly=True, default=fields.Date.context_today)
    sms_send = fields.Boolean("Sms send", default=False)

    user_id = fields.Many2one('res.users', 'Intervenant', default=lambda self: self.env.user.id)

    # rdv_ids = fields.one2many('sommeil.rdv', 'planning_id', string='RDV')

    rdv_ids = fields.Many2many('sommeil.rdv', 'sommeil_planning_rel', 'sommeil_id', 'planning_id', 'RDV', )

    state = fields.Selection((('ouvert', 'Ouvert'), ('valide', 'Validé'), ('annule', 'Annulé')), 'State',
                             default='ouvert')

    def annulation_sommeil(self, motif):
        # self.write({'motif': motif, 'state': 'annule'})
        self.write({'state': 'annule'})

    def action_annule(self):
        self.write({'state': 'annule'})

    def action_encours(self):
        self.write({'state': 'valide'})
        #self.send_sms_sommeil_planning()

    def send_sms_sommeil_planning(self):
        for o in self:
            user_partner_id = o.user_id and o.user_id.partner_id and o.user_id.partner_id.id
            user_name = o.user_id and o.user_id.name

            # message = smart_unicode(message)
            users_sms = self.env['res.users'].search([('recoi_sms_som', '=', True)])
            active_part_ids = [p.partner_id.id for p in users_sms if p.partner_id]
            if user_partner_id:
                active_part_ids = active_part_ids + [user_partner_id, ]
            active_part_ids = list(set(active_part_ids))
            message = ''

            o_name = o.name or ''
            o_patients = [l.patient_id for l in o.rdv_ids]
            o_medcins = [l.medecin_prescripteur_id for l in o.rdv_ids]
            o_examens = [l.type_examen_id for l in o.rdv_ids]
            msg = ''
            for i in range(len(o_patients)):
                msg += "\n\nPatient: "+ (o_patients[i].name or '')\
                    +"\nMedecin: "+ (o_medcins[i].name or '') \
                       + "\nExamen: " + (o_examens[i].name or '')\
                       + "\nTel: " + (o_patients[i].mobile or '')

            patients = ''
            medcins = ''
            examens = ''
            for p in o_patients:
                if p.name:
                    patients += p.name + ", "
            for p in o_medcins:
                if p.name:
                    medcins += p.name + ", "
            for p in o_examens:
                if p.name:
                    examens += p.name + ", "
            if o.state == 'valide':
                message = u"Mon Planning (" + user_name + ")\n" + "Ref: " + o_name\
                +msg
                #+ "\n" \
                          #+ "Patient: " + patients + '\n' \
                          #+ "Medecin:" + medcins + '\n' + "Examen:" + examens + '\n'

                if message and active_part_ids:
                    message = u'' + message.encode('utf-8')
                    self.env['sms.smsclient'].send_sms_msg_to_partners(active_part_ids=active_part_ids, add_msg=message)
                    o.sms_send = True

class SommeilReclamation(models.Model):
    _name = "sommeil.reclamation"
    _description = "Reclamation"
    _order = 'name'

    name = fields.Char('Objet de Réclamation', size=100)
    description = fields.Text('Description')
    users_id = fields.Many2one('res.users', 'Utilisateur', readonly=True, default=lambda obj: obj.env.user.id)
    date = fields.Date('Date', readonly=True, default=fields.Date.context_today)
    agence_id = fields.Many2one('crm.team', 'Agence', required=True)
    patient_id = fields.Many2one('res.partner', 'Patient',
                                 domain=[('type_client', '=', 'patient')],
                                 required=True)
    medecin_prescripteur_id = fields.Many2one('res.partner', 'Medecin Prescripteur',
                                              domain=[('type_client', '=', 'medecins')],
                                              required=True)
    state = fields.Selection((('ouvert', 'En cours'), ('valide', 'Validé')), 'State', readonly=True, default='ouvert')
