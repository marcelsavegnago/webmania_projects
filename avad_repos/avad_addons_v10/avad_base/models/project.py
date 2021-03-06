# -*- coding: utf-8 -*-

import time
import math
from datetime import datetime, timedelta
from django.utils.encoding import smart_str, smart_unicode

from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError, Warning
from odoo import api, fields, models, _


class ProjectAmh(models.Model):
    _inherit = "project.project"
    _description = "Acceuil"
    _order = "date_new desc"

    def _compute_sale_order(self):
        for o in self:
            o.sale_orders_count = len(o.sale_order_ids)
            
    @api.depends('status_dossier')
    def computed_related_status(self):
        for o in self:
            o.related_status_dossier = o.status_dossier if o.status_dossier else 'new'

    label_tasks = fields.Char(string='Use Tasks as', default='Suivis de la demande',
                              help="Gives label to tasks on project's kanban view.")
    ref_seq = fields.Char("Sequence")
    agence_id = fields.Many2one('crm.team', 'Agence', required=True)
    demande = fields.Selection([('vente', 'Vente'),
                                ('location', 'Location'),
                                ('seance', 'Par Séance'), ], 'Type de besoin', required=True)
    canal_avad = fields.Selection([('1', 'Appel Standard'),
                                   ('2', 'Direction'),
                                   ('3', 'Email'),
                                   ('4', 'Fax'),
                                   ('5', 'Visite directe acceuil'),
                                   ('6', 'Site web'),
                                   ('7', 'Réseaux sociaux'),
                                   ], string='Canal', default='1', required=True)
    cible = fields.Selection([('patient', 'Patient'),
                              ('proche_patient', 'Proche patient'),
                              ('vacancier', 'Vacancier'),
                              ('medecin_prescripteur', 'Médecin Prescripteur'),
                              ('medecin_traitant', 'Médecin Traitant')], 'Contact', required=True)
    patient_id = fields.Many2one('res.partner', 'Patient', domain=[('type_client', 'in', ['patient'])], required=True,
                                 track_visibility="onchange")
    medecin_prescripteur_id = fields.Many2one('res.partner', 'Medecin Prescripteur',
                                              domain=[('type_client', '=', 'medecins')],
                                              required=True, track_visibility="onchange")
    medecin_traitant_id = fields.Many2one('res.partner', 'Medecin Traitant',
                                          domain=[('type_client', '=', 'medecins')])

    date_new = fields.Date('Date courante', default=fields.Date.context_today)

    parent_id = fields.Many2one('project.project', 'Demande parente')
    child_ids = fields.One2many('project.project', 'parent_id', string='Demandes')
    av_attachment_ids = fields.Many2many('ir.attachment', 'avad_project_attachment_rel', 'avad_project_id',
                                         'attachment_id', 'Attachments')

    avad_state = fields.Selection([
        ('draft', 'Brouillon'),
        ('valid', 'Validé'),
        ('done', 'Clôturé'),
    ], "Workflow vente", default='draft')

    sale_order_ids = fields.One2many('sale.order', 'our_project_id', 'Devis/Bon commandes')
    sale_orders_count = fields.Integer('Sale orders', default=0, compute=_compute_sale_order)

    # === location fields
    #
    # location_state = fields.Selection([
    #     ('ouvert', u'Ouvert'),
    #     ('instal', u'Intallation'),
    #     ('visitr', u'Visite régulière à domicile'),
    #     ('acceuil', u'Acceuil'),
    #     ('visitr2', u'Visite régulière à domicile'),
    #     ('encours', u'En cours'),
    #     ('cloture', u'Clôturé'),
    # ], "Workflow location", default='ouvert')

    nb_mois_loc = fields.Integer("Nbr. mois")
    start_date_loc = fields.Date("Date début")
    end_date_loc = fields.Date("Date fin")

    #appareillage / desapareillage
    status_dossier = fields.Selection([
        ('appar', 'Appareillage'),
        ('desappar', 'Desappareillage')
    ], string="Status du dossier")
    related_status_dossier=fields.Selection([
        ('new','Nouveau'),
        ('appar', 'Appareillage'),
        ('desappar', 'Desappareillage')
    ], string="Status du dossier", compute=computed_related_status, store=True)
    date_appar = fields.Datetime("Date Appareillage")
    date_desappar = fields.Datetime("Date Desappareillage")
    motif_desappar = fields.Many2one("motif.desapar","Motif Desappareillage")

    # ===================

    @api.onchange('nb_mois_loc')
    def onchange_nb_mois_loc(self):
        # print("mois ====")
        for o in self:
            if o.nb_mois_loc:
                if o.start_date_loc:
                    ds = fields.Date.from_string(o.start_date_loc)
                    df = ds + timedelta(o.nb_mois_loc * 365 / 12)
                    o.end_date_loc = fields.Date.to_string(df)
                    o.date_end = fields.Date.to_string(df)
                    # print("end:", fields.Date.to_string(df))
                elif o.end_date_loc:
                    df = fields.Date.from_string(o.end_date_loc)
                    ds = df - timedelta(o.nb_mois_loc * 365 / 12)
                    o.start_date_loc = fields.Date.to_string(ds)
                    o.date_start = fields.Date.to_string(ds)
                    # print("start:", fields.Date.to_string(ds))

    @api.onchange('start_date_loc')
    def onchange_start_date_loc(self):

        for o in self:
            # print("start ====", o.start_date_loc, o.end_date_loc, o.nb_mois_loc)
            o.date_start = o.start_date_loc
            if o.start_date_loc and o.end_date_loc:
                if o.start_date_loc >= o.end_date_loc:
                    raise ValidationError(u"La date de début doit être > à celle de fin")
                ds = fields.Date.from_string(o.start_date_loc)
                df = fields.Date.from_string(o.end_date_loc)
                o.nb_mois_loc = math.ceil(float((df - ds).days) / 30.0)
                # print("mois:", math.ceil(float((df-ds).days) / 30.0))
            elif o.start_date_loc and o.nb_mois_loc:
                ds = fields.Date.from_string(o.start_date_loc)
                df = ds + timedelta(float(o.nb_mois_loc) * (365.0 / 12))
                o.end_date_loc = fields.Date.to_string(df)
                o.date_end = fields.Date.to_string(df)
                # print("end:", fields.Date.to_string(df))

    @api.onchange('end_date_loc')
    def onchange_end_date_loc(self):
        # print("end ====")
        for o in self:
            o.date_end = o.end_date_loc
            if o.start_date_loc and o.end_date_loc:
                if o.start_date_loc >= o.end_date_loc:
                    raise ValidationError(u"La date de fin doit être > à celle de début")
                ds = fields.Date.from_string(o.start_date_loc)
                df = fields.Date.from_string(o.end_date_loc)
                # print("mois:",math.ceil(float((df - ds).days) / 30.0))
                o.nb_mois_loc = math.ceil(float((df - ds).days) / 30.0)
            elif o.end_date_loc and o.nb_mois_loc:
                df = fields.Date.from_string(o.end_date_loc)
                ds = df - timedelta(float(o.nb_mois_loc) * (365.0 / 12))
                o.start_date_loc = fields.Date.to_string(ds)
                o.date_start = fields.Date.to_string(ds)
                # print("satart:", fields.Date.to_string(ds))

    @api.onchange('patient_id')
    def onchange_remplir_name(self):
        for o in self:
            if not o.name:
                o.name = o.patient_id and o.patient_id.name

    # @api.onchange("avad_state")
    # def action_attente_avad(self):
    #     self.write({'avad_state': 'attente'})
    #     warning = ''
    #     for o in self:
    #         if not o.doc_count:
    #             warning += '\nProjet ' + o.ref_seq
    #     if len(warning):
    #         return {'warning': {
    #             'title': _('Acertisement!'),
    #             'message': _('Il faut ajouter les pieces jointes!'+warning),
    #         },
    #         }

    @api.multi
    def action_validate_avad(self):
        self.write({'avad_state': 'valid'})

    @api.multi
    def send_sms_msg(self, add_msg=''):
        gateway = self.env['sms.smsclient'].search([])
        gateway = gateway[0] if len(gateway) else False
        for o in self:
            try:
                prs_p = o.medecin_prescripteur_id
                clien_p = o.patient_id
                trait = o.medecin_traitant_id
                seq_p = o.ref_seq
                users_sms = self.env['res.users'].search([('recoi_sms', '=', True)])

                seq_str = smart_str(seq_p or "''")
                clien_p_str = smart_str(("\nCLT: " + clien_p.name) if clien_p else '')
                pres_p_str = smart_str(("\nMP: " + prs_p.name) if prs_p else '')
                trait_str = smart_str(("\nMT: " + trait.name) if trait else '')

                msg = smart_str("Bonjour,\nLe dossier ") + seq_str + smart_str(" est valide")
                msg_med = msg + clien_p_str + pres_p_str + trait_str
                msg_avad = msg_med + smart_str(("\n" + add_msg) if len(add_msg or '') else '')

                # Send SMS to avad team
                active_part_ids = [p.partner_id.id for p in users_sms if p.partner_id]
                active_part_ids = list(set(active_part_ids))
                sms_prj = self.with_context(active_part_ids=active_part_ids).env["part.sms.lead"].create({
                    'gateway': gateway and gateway.id or False,
                    'body': msg_avad,
                })
                sms_prj.sms_mass_send()

                # send SMS to medcins
                active_part_ids = [p.id for p in [prs_p, trait] if p]
                active_part_ids = list(set(active_part_ids))
                sms_prj = self.with_context(active_part_ids=active_part_ids).env["part.sms.lead"].create({
                    'gateway': gateway and gateway.id or False,
                    'body': msg_med,
                })
                sms_prj.sms_mass_send()
            except Exception as e:
                print("Some SMS not sended ===", e)

    @api.multi
    def send_sms_msg_suivis(self, add_msg=''):
        gateway = self.env['sms.smsclient'].search([])
        gateway = gateway[0] if len(gateway) else False
        for o in self:
            try:
                prs_p = o.medecin_prescripteur_id
                trait = o.medecin_traitant_id
                users_sms = self.env['res.users'].search([('recoi_sms', '=', True)])
                active_part_ids = [p.partner_id.id for p in users_sms if p.partner_id] + [p.id for p in [prs_p, trait]
                                                                                          if p]
                sms_prj = self.with_context(active_part_ids=active_part_ids).env["part.sms.lead"].create({
                    'gateway': gateway and gateway.id or False,
                    'body': smart_str(add_msg),
                })
                sms_prj.sms_mass_send()

            except Exception as e:
                print("Some SMS not sended ===", e)

    @api.model
    def create(self, values):
        res = super(ProjectAmh, self).create(values)
        for o in res:
            if not o.ref_seq:
                try:
                    seq = self.env['ir.sequence'].next_by_code('res.project.avad.seq1') or False
                    seq = str(o.patient_id.name) + '/' + str(datetime.now().day) + '/' + str(
                        datetime.now().month) + '/' + str(datetime.now().year) + '/' + seq
                    o.ref_seq = seq
                    o.name = seq
                except:
                    raise ValidationError("Le sequence code = 'res.project.avad.seq1' n'existe pas dans la base.")
        return res

    # @api.multi
    # def write(self, values):
    #     if 'medecin_prescripteur_id' in values:
    #         pass
    #     if 'medecin_traitant_id' in values:
    #         pass
    #
    #     res = super(ProjectTask, self).write(values)
    #     return res

    @api.constrains('medecin_prescripteur_id')
    def constr_medc_pres(self):
        for o in self:
            print("==T=", o, o.id, o.medecin_prescripteur_id)
            for f in o.message_follower_ids:
                if o.medecin_prescripteur_id and f.partner_id.id == o.medecin_prescripteur_id.id:
                    break
            else:
                if o.medecin_prescripteur_id:
                    self.env['mail.followers'].create({'partner_id': o.medecin_prescripteur_id.id, 'res_model': 'project.project',
                            'res_id': o.id})

    @api.constrains('medecin_traitant_id')
    def constr_medc_traitant(self):
        for o in self:
            print("==T=", o, o.id, o.medecin_traitant_id)
            for f in o.message_follower_ids:
                if o.medecin_traitant_id and f.partner_id.id == o.medecin_traitant_id.id:
                    break
            else:
                if o.medecin_traitant_id:
                    self.env['mail.followers'].create(
                    {'partner_id': o.medecin_traitant_id.id, 'res_model': 'project.project',
                     'res_id': o.id})

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if not default:
            default = {}
        default['ref_seq'] = False
        default['avad_state'] = 'draft'
        res = super(ProjectAmh, self).copy(default=default)
        return res

    @api.onchange('patient_id')
    def onchange_partner_id(self):
        for o in self:
            o.partner_id = o.patient_id

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ Override read_group to always display all states. """
        my_context = self._context or {}
        # my_grp_by = my_context.get("defaul_kanban_grp", False)
        # if my_grp_by:
        #    groupby[0] = my_grp_by
        # print("==== grp by", groupby)
        if groupby and groupby[0] == "avad_state":
            # Default result structure
            states = [('draft', 'Brouillon'),
                      ('valid', 'Validé'),
                      ('done', 'terminé'), ]

            read_group_all_states = [{
                '__context': {'group_by': groupby[1:]},
                '__domain': domain + [('avad_state', '=', state_value)],
                'avad_state': state_value,
                'avad_state_count': 0,
            } for state_value, state_name in states]
            # Get standard results
            read_group_res = super(ProjectAmh, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                                orderby=orderby)
            # Update standard results with default results
            result = []
            for state_value, state_name in states:
                res = filter(lambda x: x['avad_state'] == state_value, read_group_res)
                if not res:
                    res = filter(lambda x: x['avad_state'] == state_value, read_group_all_states)
                if state_value == 'cancel':
                    res[0]['__fold'] = True
                res[0]['avad_state'] = [state_value, state_name]
                result.append(res[0])
            return result

        else:
            return super(ProjectAmh, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                      orderby=orderby)


class ProjectTask(models.Model):
    _inherit = "project.task"
    _order = 'id desc'

    @api.depends('stage_id')
    def compute_type_stage_avad(self):
        for o in self:
            if o.stage_id:
                o.type_stage_avad = o.stage_id.type_stage

    @api.depends('poids', 'taille')
    def _compute_imc(self):
        for o in self:
            o.imc = (float(o.poids) / float(o.taille ** 2)) if (o.taille and o.poids) else 0

    @api.depends('stage_id', 'type_rapport', 'objet_suivi_id')
    def _compute_name_task(self):
        for o in self:
            name = o.objet_suivi_id and o.objet_suivi_id.name or ' '
            if o.type_stage_avad == 'rapport':
                name = 'Rapport / ' + (o.type_rapport or '')
            o.name = name

    name = fields.Char("Nom", compute=_compute_name_task, store=True, required=False)
    show_portal = fields.Selection([
        ('afficher', 'Afficher'),
        ('masquer', 'Masquer'),
    ], default='afficher', string='Portail')
    type_stage_avad = fields.Selection([
        ('appar', 'Appareillage'),
        ('suivi', 'Suivis'),
        ('rapport', 'Rapport'),
        ('desappar', 'Desappareillage'),
        ('qualite', 'Qualite'),
        ('maintenance', 'Maintenance'),
        ('autre', 'Autre'),
    ], default='autre', string='Type', compute=compute_type_stage_avad)

    objet_suivi_id = fields.Many2one("objet.suivi", string="Objet", required=False)
    objet_suivi_ids = fields.Many2many("objet.suivi", string="Objets", related="stage_id.objet_suivi_ids")
    type_rapport = fields.Selection([
        ('O2', 'O2'),
        ('PPC', 'PPC'),
        ('VNI', 'VNI'),
        ('AGS', 'AGS'),
        ('PN', 'PN'),
        ('AOTI', 'AOTI'),
    ], "Type fiche")

    comment = fields.Text("Commentaire")
    # PPC-- Fields
    date_visite = fields.Date("Date de visite", default=fields.Date.context_today)
    lieu = fields.Selection([
        ('showroom', 'Showroom'),
        ('domicile', 'À domicile'),
        ('clinique', 'Clinique'),
        ('hopital', 'Hôpital'), ], string="Lieu")

    ddn = fields.Date("Date de naissance", required=False,
                      default=lambda r: r.project_id and r.project_id.patient_id and r.project_id.patient_id.ddn or 0)
    iah_initial = fields.Integer("IAH Initial", default=lambda
        r: r.project_id and r.project_id.patient_id and r.project_id.patient_id.iah_initial or 0)
    poids = fields.Float("Poids (kg)", default=lambda
        r: r.project_id and r.project_id.patient_id and r.project_id.patient_id.poids or 0)
    taille = fields.Float("Taille (m)", default=lambda
        r: r.project_id and r.project_id.patient_id and r.project_id.patient_id.taille or 0)
    imc = fields.Float("IMC", compute=_compute_imc)
    date_intal_vni = fields.Date("Date d'installation")

    type_appareil = fields.Selection([
        ('dsp', 'DreamStation Philips'),
        ('aarm', 'AirSense 10 AutoSet | ResMed'),
        ('isb', 'iSleep 20i - Breas'), ], string="Type d'appareil", required=False)
    num_serie = fields.Char("N série", required=False)
    type_masque = fields.Selection([('1', 'Facial'), ('2', 'Nasal'), ('3', 'Narinaire'), ('4', 'Nano')],
                                   string="Type de masque", required=False)
    marque_masque = fields.Selection([('1', 'Philips'), ('2', 'ResMed'), ('3', 'Currative')], string="Marque du masque",
                                     required=False)
    humidification = fields.Selection([('1', 'Oui'), ('2', 'Non')], string="Humidification", required=False)
    cir_chauff = fields.Selection([('1', 'Oui'), ('2', 'Non')], string="Circuit chauffant", required=False)

    date_db = fields.Date("Date début", required=False)
    date_fn = fields.Date("Date fin", required=False)
    dur_utlis = fields.Integer("Durée d'utilisation /j", required=False)
    dur_someil = fields.Integer("Durée sommeil patient", required=False)
    tolerance = fields.Selection([('1', 'Oui'), ('2', 'Non')], string="Tolérance", required=False)
    motif_tolerance = fields.Char("Motif", required=False)
    moy_utlis_vni = fields.Integer("Moyenne d'Utilisation (h / jour)", required=False)
    vlm_moy_vni = fields.Float("Volume moyen (mL)", required=False)
    iah_resid_vni = fields.Float("IAH Résiduel", required=False)
    freq_moy_vni = fields.Float("Fréquence moyenne (c./min)", required=False)
    nb_hrs_vni = fields.Integer("Nombre d'heures", required=False)

    fuite = fields.Selection([('1', 'Oui'), ('2', 'Non')], string="Fuite", required=False)
    taux_fuite = fields.Float("Taux fuite (Lpm)", required=False)
    fuite_origine = fields.Selection([('1', 'Buccales'), ('2', 'Mauvais positionnement'), ('3', 'Autres')],
                                     string="Origine", required=False)

    pres_p = fields.Float("Pression préscrite", required=False)
    pres_min = fields.Float("Pression min (cmH2O)", required=False)
    pres_moy = fields.Float("Pression (Moy 95%)", required=False)
    pres_max = fields.Float("Pression max (cmH2O)", required=False)
    rampe = fields.Integer("Rampe (min)", required=False)

    iah_resid = fields.Float("IAH résiduel", required=True)
    date_pr_visit = fields.Date("Date prochaine visite ", required=False)
    conclusion = fields.Text("Conclusion")
    # END PPC
    # VNI
    type_vst = fields.Selection([
        ('msp', 'Mise en place'),
        ('ctrl', 'Contrôle'),
        ('corrective', 'Corrective'), ], string="Type de visite", required=False)

    modele_mat_vni = fields.Selection(
        [('1', 'Ventilateur VIVO 40'), ('2', 'Bipap Avaps C Series'), ('3', 'Legendaire'), ('4', 'BiPAP Synchrony 2'),
         ('5', 'Bipap pro BiFlex '), ('6', 'Ventillateur Trilogy 100'), ('7', 'Ventilateur HOME 2 ')], string="Modèle",
        required=False)
    marque_mat_vni = fields.Selection([('1', 'Philips'), ('2', 'Resmed'), ('3', 'AIROX'), ('4', 'Breas')],
                                      string="Marque", required=False)
    humd_mat_vni = fields.Selection([('1', 'Oui'), ('2', 'Non'), ('3', 'Parfois'), ('4', 'Rarement')],
                                    string="Humidification", required=False)
    oxy_mat_vni = fields.Char(string="Oxygénothérapie associée", required=False)

    interface_mas_vni = fields.Selection([('1', 'Facial'), ('2', 'Nasal')], string="Interface", required=False)
    modele_mas_vni = fields.Selection([('1', 'Amara View'), ('2', 'Quattro fx'), ('3', 'AirFit N20')], string="Modèle",
                                      required=False)
    marque_mas_vni = fields.Selection([('1', 'Philips'), ('2', 'Resmed'), ('3', 'Curative')], string="Marque",
                                      required=False)
    tmasq_mas_vni = fields.Selection([('1', 'Small'), ('2', 'Meduim'), ('3', 'Large')], string="Taille du masque",
                                     required=False)

    ipap_reg_vni = fields.Float("IPAP (cmH2O)", required=False)
    epap_reg_vni = fields.Float("EPAP (cmH2O)", required=False)
    freq_reg_vni = fields.Float("Fréquence (c./min)", required=False)

    timax_mode_vni = fields.Float("Timax (sec.)", required=False)
    timin_mode_vni = fields.Float("Timin (sec.)", required=False)
    pente_mode_vni = fields.Float("Pente (ms)", required=False)

    # O2
    type_vst_o2 = fields.Selection(
        [('1', 'Visite régulière'), ('5', 'Installation Interne'), ('29', 'Dépannage'), ('26', 'Entretien'),
         ('23', 'RD')], string="Type de visite", required=False)
    modele_apr_o2 = fields.Selection(
        [('1', 'EVERFLO'), ('2', 'Dévilbis'), ('3', 'VISIONAIRE'), ('4', 'NewLife'), ('5', 'Bouteil O2'),
         ('6', 'Cuve Liquide'), ('7', 'Portable Liquide'), ('55', 'Appareil portable électrique')],
        string="Modèles d'appareils")
    num_ser_o2 = fields.Char("Numéro de série")
    com_apr_o2 = fields.Char("Compteur d'appareil")

    tabac_o2 = fields.Selection([('1', 'Oui'), ('2', 'Non')], "Tabac")
    hosp_o2 = fields.Selection([('1', 'Oui'), ('2', 'Non')], "Hospitalisations")
    phot_o2 = fields.Selection(
        [('1', 'BPCO'), ('2', 'SLA'), ('3', 'Myopathie'), ('4', 'Fibrose pulmonaire'), ('5', 'Obésité'),
         ('66', 'Autre')], "Pathologie")
    nbr_cig_o2 = fields.Integer("Nombre de cigarettes/jour")
    duree_o2 = fields.Float("Durée")

    typeox_o2 = fields.Selection([('1', 'Concentrateur'), ('2', 'Liquide'), ('3', 'Bouteil')], "Type Oxygène")
    debit_o2 = fields.Float("Débit O² (L/min)")
    nhours_o2 = fields.Float("Nombre d'heure (o²) CONTINUE")

    sao2_sans_o2 = fields.Char("SaO2 %")
    fcbpm_sans_o2 = fields.Char("FC bpm")
    sao2_sous_o2 = fields.Char("SaO2 %")
    fcbpm_sous_o2 = fields.Char("FC bpm")

    @api.onchange('stage_id')
    def on_change_stage_id_avad(self):
        for o in self:
            objet_ids = []
            if o.stage_id:
                objet_ids = [l.id for l in o.stage_id.objet_suivi_ids]

            return {
                'domain': {
                    'objet_suivi_id': [('id', 'in', objet_ids)]
                }
            }

    @api.onchange('project_id')
    def my_onchange_project(self):
        for o in self:
            if o.project_id:
                if o.project_id.patient_id:
                    o.ddn = o.project_id.patient_id.ddn
                    o.iah_initial = o.project_id.patient_id.iah_initial
                    o.poids = o.project_id.patient_id.poids
                    o.taille = o.project_id.patient_id.taille
                    o.imc = o.project_id.patient_id.imc

    @api.multi
    def write(self, values):
        res = super(ProjectTask, self).write(values)
        return res

    def send_msg_rapport(self):
        for o in self:
            if (o.stage_id and o.stage_id.type_stage == 'rapport') and o.type_rapport == 'PPC':
                our_project_id = o.project_id
                if our_project_id:
                    tm = ''
                    civ = ''
                    if o.type_masque:
                        tm = dict(self._fields['type_masque'].selection).get(o.type_masque)
                    if our_project_id.medecin_prescripteur_id:
                        civ = dict(self.env['res.partner']._fields['civilite'].selection).get(
                            our_project_id.medecin_prescripteur_id.civilite)

                    msg_suiv = "Cher(e) " + str(civ or '').capitalize() + ','
                    msg_suiv += '\nDate: ' + str(o.date_visite or '')
                    msg_suiv += '\nPAT: ' + str(our_project_id.patient_id.name or '')
                    msg_suiv += '\nTTT: ' + str(o.type_rapport or '')
                    msg_suiv += '\nIAH: ' + '%s' % (o.iah_resid or '')
                    msg_suiv += '\nPmin: ' + '%s' % (o.pres_min or '')
                    msg_suiv += '\nPmax: ' + '%s' % (o.pres_max or '')
                    msg_suiv += '\nMasque: ' + str(tm or '')
                    our_project_id.send_sms_msg_suivis(msg_suiv)
                    # print("Msg envoyee :\n",msg_suiv)

    @api.model
    def create(self, vals):
        res = super(ProjectTask, self).create(vals)
        res.send_msg_rapport()
        return res

    # def print_ppc_rapport(self):


class PriecTaskType(models.Model):
    _inherit = "project.task.type"

    objet_suivi_ids = fields.Many2many("objet.suivi", string="Objets")
    type_stage = fields.Selection([
        ('appar', 'Appareillage'),
        ('suivi', 'Suivis'),
        ('rapport', 'Rapport'),
        ('desappar', 'Desappareillage'),
        ('qualite', 'Qualite'),
        ('maintenance', 'Maintenance'),
        ('autre', 'Autre'),
    ], default='autre', string='Type', required=True)
