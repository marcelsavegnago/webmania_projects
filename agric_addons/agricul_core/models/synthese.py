# -*- coding: utf-8 -*-

import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

MOIS_PR = {'9': 'sept',
           '10': 'oct',
           '11': 'nov',
           '12': 'dec',
           '1': 'jan',
           '2': 'fev',
           '3': 'mars',
           '4': 'avr',
           '5': 'mai',
           '6': 'juin',
           '7': 'juil',
           '8': 'aout',
           }


class Synthese(models.Model):
    _name = 'amh.synthese'

    @api.depends('ecart_ligne', 'ecart_plant')
    def _compute_1(self):
        for o in self:
            o.density_str = str(o.ecart_ligne or 0) + 'm x ' + str(o.ecart_plant or 0) + 'm'

    @api.depends('ecart_plant', 'nb_ramp_line', 'nombre_dist_arb')
    def _get_ecarts(self):
        for o in self:
            try:
                o.ecart_gtrs_cal = o.ecart_plant * o.nb_ramp_line / o.nombre_dist_arb
            except:
                o.ecart_gtrs_cal = 0

    @api.depends('ecart_plant', 'nb_ramp_line', 'nombre_dist_arb', )
    def _get_dist_arbr(self):
        for o in self:
            try:
                o.nombre_dist_arb_cal = o.ecart_plant / o.ecart_gtrs_cal * o.nb_ramp_line
            except:
                o.nombre_dist_arb_cal = 0

    @api.depends('culture_irg', 'culture_irg.densite_x', 'culture_irg.densite_y',
                 'ecart_ligne', 'ecart_plant', 'nb_ramp_line', 'nombre_dist_arb',
                 'superficie_eqp', 'q_goutteur')
    def _compute_super_gtr(self):
        for o in self:
            super_goutteur = 0
            try:
                super_goutteur = (o.ecart_ligne * o.ecart_plant) / \
                                 ((o.ecart_plant / o.ecart_gtrs_cal) * o.nb_ramp_line)
            except:
                super_goutteur = 0
            o.super_goutteur = super_goutteur
            try:
                o.q_tot_parcelle = ((o.superficie_eqp / super_goutteur) * o.q_goutteur) / 1000
            except:
                o.q_tot_parcelle = 0
            try:
                pf_qg_sg = o.q_goutteur / super_goutteur
                o.pf_qg_sg = pf_qg_sg
            except:
                o.pf_qg_sg = 0

    @api.depends('culture_irg', 'culture_irg.densite_x', 'culture_irg.densite_y',
                 'ecart_ligne', 'ecart_plant', 'nb_ramp_line', 'nombre_dist_arb',
                 'superficie_eqp', 'q_goutteur')
    def _compute_durees(self):
        for o in self:
            try:
                duree_irg_sec_jr = o.bbmmj_val / o.pf_qg_sg
                o.duree_irg_sec_jr = duree_irg_sec_jr
                hh, mm = int(duree_irg_sec_jr), int((duree_irg_sec_jr - int(duree_irg_sec_jr)) * 60)
                o.duree_irg_sec_jr_h = str(hh).zfill(2) + "h" + str(mm).zfill(2) + "min"
                o.duree_tot_irg = duree_irg_sec_jr * o.q_sec_reel
            except Exception as e:
                print("Exception AMH: _compute_durees, ", e)

    @api.multi
    def dummy(self):
        pass

    @api.depends('culture_irg', 'culture_irg.densite_x', 'culture_irg.densite_y')
    def _compute_ecart_ligne_plant(self):
        for o in self:
            o.ecart_ligne = o.culture_irg and o.culture_irg.densite_x or 0
            o.ecart_plant = o.culture_irg and o.culture_irg.densite_y or 0

    @api.depends('goutteur_id', 'choosen_pvc', 'nb_post_secteur', 'superficie_eqp')
    def _compute_nb_sec_theo(self):
        for o in self:
            msg = ""
            try:
                msg = u"Q secteur théorique est 0 !"
                nb_sec_theo = float(o.q_tot_parcelle or 0) / o.q_sec_theo
                nb_sec_reel = math.ceil(nb_sec_theo)
                o.nb_sec_theo = nb_sec_theo
                o.nb_sec_reel = nb_sec_reel
                msg = u"Q secteurs réel est 0 !"
                o.q_sec_reel = o.q_tot_parcelle / nb_sec_reel
                o.surface_secteur = o.superficie_eqp / nb_sec_reel
                o.nb_van_tot = o.nb_post_secteur * nb_sec_reel
                msg = u"Q secteurs réel ou\n Nombre de poste ( Nbr de vanne par secteur) est 0 !"
                o.q_post = (o.q_tot_parcelle / nb_sec_reel) / o.nb_post_secteur
                msg = u"Q secteurs réel ou/et\n Nombre de poste ( Nbr de vanne par secteur) est 0 !"
                o.surface_post = (o.superficie_eqp / nb_sec_reel) / o.nb_post_secteur
                o.duree_tot_irg = o.duree_irg_sec_jr * nb_sec_reel
                o.message_error = False
            except Exception as e:
                print("Exception AMH:", e)
                o.message_error = "Erreur lors le calcul:\n" + msg

    def _compute_name_synt(self):
        for o in self:
            o.name = o.culture_irg.name or ''

    name = fields.Char("Nom", compute=_compute_name_synt)
    project_id = fields.Many2one('project.project', "Projet")
    culture = fields.Many2one("amh.culture", string="Culture.", related='culture_irg.amh_culture_id', store=True)
    culture_irg = fields.Many2one("amh.culture.irriguer", string="Culture")
    superficie_eqp = fields.Float(string="SUPERFICIE A EQUIPER m2")
    density_str = fields.Char(string=u"Densité", compute=_compute_1)
    type_goutteur = fields.Char('Type de goutteur')
    goutteur_id = fields.Many2one("product.template", string="Goutteur")
    q_goutteur = fields.Float('Q goutteur')
    press_gtr_dist = fields.Float("Pression de service du distributeur")
    coeiff_xk = fields.Float('COEIFF X/K')
    date_validity = fields.Date("Date validitée")  # gtr
    ecart_gtrs_cal = fields.Float("Ecartement entre goutteurs CALCULE", compute=_get_ecarts)
    nombre_dist_arb = fields.Float("Nombre de  du distributeur / arbre: THIORIQUE")
    nombre_dist_arb_cal = fields.Float("Nombre de  du distributeur / arbre", compute=_get_dist_arbr)
    ecart_ligne = fields.Float(string=u"Ecartement entre ligne", compute=_compute_ecart_ligne_plant, store=True)
    ecart_plant = fields.Float(string=u"Ecartement entre plants", compute=_compute_ecart_ligne_plant, store=True)
    nb_ramp_line = fields.Selection([(1,'1'),(2,'2')],string=u"Nombre de rampe/ligne")
    super_goutteur = fields.Float("Superficie/goutteur", compute=_compute_super_gtr)
    q_tot_parcelle = fields.Float("Q TOTAL de la parcelle", compute=_compute_super_gtr)
    # choosen PVC
    choosen_pvc = fields.Many2one('product.template', string="PVC", domain=[('type_article', '=', 'pvc')])
    q_sec_theo = fields.Float("Q secteur théorique", related="choosen_pvc.debit_max")
    nb_sec_theo = fields.Float("Nombre de sect théorique", compute=_compute_nb_sec_theo)
    nb_sec_reel = fields.Integer("Nombre de sect réel", compute=_compute_nb_sec_theo)
    q_sec_reel = fields.Float("Q secteur réel", compute=_compute_nb_sec_theo)
    surface_secteur = fields.Float("Surface secteur", compute=_compute_nb_sec_theo)
    nb_post_secteur = fields.Integer("Nombre de poste ( Nbr de vanne par secteur)")
    nb_van_tot = fields.Float("Nombre de poste ( Nbr vannes) total", compute=_compute_nb_sec_theo)
    q_post = fields.Float("Q poste", compute=_compute_nb_sec_theo)
    surface_post = fields.Float("Surface de poste", compute=_compute_nb_sec_theo)
    pf_qg_sg = fields.Float("Pf  =  Qg/ Sg  Pluviometrie  calculée (mm/h)", compute=_compute_super_gtr)
    duree_irg_sec_jr = fields.Float("Durée d'irrigation par secteur par jour  (T)", compute=_compute_durees)
    duree_irg_sec_jr_h = fields.Char("Durée d'irrigation par secteur par jour(T) HH:MM", compute=_compute_durees)
    duree_tot_irg = fields.Float("Durée Total d'rrigation", compute=_compute_durees)
    message_error = fields.Char('Message', compute=_compute_nb_sec_theo)

    eto_val = fields.Float('Et0', compute='_compute_params')
    kc_val = fields.Float('Kc', compute='_compute_params')
    kr_val = fields.Float('Kr', compute='_compute_params')
    ea_val = fields.Float('Ea = 90%', compute='_compute_params')
    bbmmj_val = fields.Float('Bb mm/j', compute='_compute_params')

    @api.depends('project_id.mois_pointe', 'culture_irg')
    def _compute_params(self):
        for o in self:
            if o.culture_irg:
                mois_point = o.project_id and o.project_id.mois_pointe or '7'
                mois_point = MOIS_PR.get(mois_point, 'juil')
                et0 = o.project_id.amh_region_lines.filtered(lambda r: r.name == 'et0mmjr')
                params_culture = o.project_id.culture_prj_lines.filtered(
                    lambda r: r.amh_culture_prj_id.id == o.culture_irg.amh_culture_id.id)
                kc = params_culture.filtered(lambda r: r.name == 'kc')
                kr = params_culture.filtered(lambda r: r.name == 'kr')
                ea = params_culture.filtered(lambda r: r.name == 'ea')
                kc = kc and getattr(kc[0], mois_point, 0) or 0
                kr = kr and getattr(kr[0], mois_point, 0) or 0
                ea = ea and getattr(ea[0], mois_point, 0) or 0
                et0 = et0 and getattr(et0[0], mois_point, 0) or 0
                o.eto_val = et0
                o.kc_val = kc
                o.kr_val = kr
                o.ea_val = ea
                o.bbmmj_val = float(et0 * kc * kr) / float(ea)

    @api.onchange('goutteur_id', 'culture_irg')
    def onchange_fct1(self):
        for o in self:
            if o.culture_irg:
                o.superficie_eqp = o.culture_irg.superficie * 10000
            if o.goutteur_id:
                o.q_goutteur = o.goutteur_id.q_moyen
                o.date_validity = o.goutteur_id.validate_date
                o.press_gtr_dist = o.goutteur_id.pression_service
                o.coeiff_xk = o.goutteur_id.exposant
