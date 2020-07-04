# -*- coding: utf-8 -*-

import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
# from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

from datetime import datetime

MOIS_REGION = [
    ('9', 'Sept.'),
    ('10', 'Oct.'),
    ('11', 'Nov.'),
    ('12', 'Déc.'),
    ('1', 'Jan.'),
    ('2', 'Fev.'),
    ('3', 'Mars'),
    ('4', 'Avr.'),
    ('5', 'Mai'),
    ('6', 'Juin'),
    ('7', 'Jui.'),
    ('8', 'Août'),
]
MONTH_DAYS = {
    '9': 30,
    '10': 31,
    '11': 30,
    '12': 31,
    '1': 31,
    '2': 28,
    '3': 31,
    '4': 30,
    '5': 31,
    '6': 30,
    '7': 31,
    '8': 31,
}

NAME_PRECALCUL_CULTURE = [
    ('kc', 'Kc'),
    ('kr', 'Kr (**)'),
    ('supha', 'Super.(ha)'),
    ('ea', 'Ea'),
    ('be', 'Be (m³)'),
    ('btc_cult', 'Besoins totaux (en m3) (*)'),
]

NAME_PRECALCUL_DOWN2 = [('btc', "Besoins totaux des cultures (en m3)"),
                        ('dexploi', "Débit d'exploitation (en m3/h)"),
                        ('nbh', "Nbre d'heures de fonct./jour"),
                        ('vold', "Volume disponible (en m3)"),
                        ('bilanrb', 'Bilan ressources-besoins '),
                        ('volmp', "Volume disp du mois precedent (en m³)"),
                        ('bilanrbb', 'Bilan ressources-besoins (Bassin) ')]


class ProjectProject(models.Model):
    _inherit = "project.project"
    _order = "id desc"

    def _compute_counts(self):
        for o in self:
            o.nb_cultures_irg = len(o.amh_cultures_irg)

    @api.depends("amh_cultures_irg", "amh_cultures_irg.superficie")
    def _get_superfice_a_eq(self):
        for o in self:
            superficie_tot = [
                int((round(l.superficie or 0, 5) * 10000)) for l in o.amh_cultures_irg]
            #print(superficie_tot)
            superficie_tot = sum(superficie_tot)
            #print(superficie_tot)
            if superficie_tot:
                x = superficie_tot
                ha = int(float(x) / 10000)
                reste = x - (ha * 10000)
                a = int(reste / 100)
                reste = reste - (a * 100)
                ca = int(reste)
                o.super_nette_eqp = "{} ha {} a {} ca".format(str(ha), str(a).zfill(2), str(ca).zfill(2)[:2])

    label_tasks = fields.Char(default="Tâches")
    state = fields.Selection([('new', 'Nouveaux  Dossiers'),
                              ('qalified', "Dossiers en attente d'approbation"),
                              ('won', 'Dossiers approuvés'),
                              ('installed', 'Dossiers installés'),
                              ('lost', 'Dessiers Pérdus')], string="state", default='new')
    douar = fields.Char(string="Douar")
    commune = fields.Char(string="Commune Rurale")
    caidat = fields.Char(string="Caidat")
    cercle = fields.Char(string="Cercle")
    province = fields.Char(string="Province")
    amh_region_id = fields.Many2one('amh.region', string='Région')
    amh_region_lines = fields.One2many('amh.region.line', 'project_id', string="R Lignes")
    amh_cultures_irg = fields.One2many('amh.culture.irriguer', 'project_id', string="Cultures à irriguer")
    nb_cultures_irg = fields.Integer('Nb cults irrg', compute=_compute_counts)
    cooperative = fields.Char(string=u"Coopérative")
    texture = fields.Selection([
        ('ARGILEUX', 'ARGILEUX'),
        ('LIMONEUX', 'LIMONEUX'),
        ('SABLEUX', 'SABLEUX'),
        ('ARGILO-LIMONEUX', 'ARGILO-LIMONEUX'),
        ('LIMONO-SABLEUX', 'LIMONO-SABLEUX'),
    ],
        string="Texture")
    premiablite = fields.Many2one('amh.caracts.perm',string="Perméabilité", help="exemple 6 mm")
    typ_terrain = fields.Selection([
        ('TERRAIN PLAT', 'TERRAIN PLAT'),
        ('TERRAIN ACCIDENTE', 'TERRAIN ACCIDENTE'),
        ('LEGERE PENTE', 'LEGERE PENTE'),
    ], string="Terrain topographie", help="exemple Terrain plat")
    amh_puit_ids = fields.One2many('amh.puits', 'project_id', string="Puits")
    mois_pointe = fields.Selection(MOIS_REGION, default='7', string='Mois Pointe')
    descrpition_puits = fields.Text("Description puits")

    culture_prj_lines = fields.One2many('amh.culture.line', 'project_id', string="Mois cultures")
    dynm_precalcul_lines = fields.One2many('amh.precalcul.name', 'project_id', string="Bottom lines")
    dynm_precalcul_down2_lines = fields.One2many('amh.precalcul.down2', 'project_id', string="Bottom bilans")
    resource_eau_dispo = fields.Float("Resource en eau disponible")
    conserver_cal = fields.Boolean("Conserver Nbre heure disponible", default=False)

    # Synthese
    sytheses_prj = fields.One2many('amh.synthese', 'project_id', string="Syntheses")
    super_tot_printed = fields.Char("Supérficie totale")
    super_nette_eqp = fields.Char("Superficie nette à équiper", compute=_get_superfice_a_eq)

    # def _get_sequence(self):
    #     o.sequence_agric = self.env['ir.sequence'].next_by_code('project.project.agricul') or ''


    #sequence_agric = fields.Char('Sequence', default=_get_sequence)
    sequence_agric = fields.Char('Sequence')

    # rapport infos
    date_report = fields.Date("Date tirage dossier")
    nom_benif_report = fields.Char("Nom du bénéficiaire")
    num_dossier_report = fields.Char("N° du dossier")
    spr_nette_report = fields.Char("Superficie Nette")
    address_agric_report = fields.Char("Adresse exploitation agricole")
    prefecture_report = fields.Char("Préfecture")

    def get_info_point_report(self):
        infos = []
        for o in self:
            if o.amh_cultures_irg:
                uniq_clts = [irg.amh_culture_id.id for irg in o.amh_cultures_irg if irg.amh_culture_id]
                uniq_clts = list(set(uniq_clts))
                cultures = self.env['amh.culture'].browse(uniq_clts)
                mois_pointe = o.mois_pointe
                if not mois_pointe:
                    continue
                for cult in cultures:
                    et0 = o.amh_region_lines.filtered(lambda r: r.name == 'et0mmjr')
                    kc = o.culture_prj_lines.filtered(lambda r: r.amh_culture_prj_id.id == cult.id and r.name == 'kc')
                    kr = o.culture_prj_lines.filtered(lambda r: r.amh_culture_prj_id.id == cult.id and r.name == 'kr')
                    ea = o.culture_prj_lines.filtered(lambda r: r.amh_culture_prj_id.id == cult.id and r.name == 'ea')
                    bb = 0
                    if mois_pointe == '1':
                        et0, kc, kr, ea = et0.jan, kc.jan, kr.jan, ea.jan
                    if mois_pointe == '2':
                        et0, kc, kr, ea = et0.fev, kc.fev, kr.fev, ea.fev
                    if mois_pointe == '3':
                        et0, kc, kr, ea = et0.mars, kc.mars, kr.mars, ea.mars
                    if mois_pointe == '4':
                        et0, kc, kr, ea = et0.avr, kc.avr, kr.avr, ea.avr
                    if mois_pointe == '5':
                        et0, kc, kr, ea = et0.mai, kc.mai, kr.mai, ea.mai
                    if mois_pointe == '6':
                        et0, kc, kr, ea = et0.juin, kc.juin, kr.juin, ea.juin
                    if mois_pointe == '7':
                        et0, kc, kr, ea = et0.juil, kc.juil, kr.juil, ea.juil
                    if mois_pointe == '8':
                        et0, kc, kr, ea = et0.aout, kc.aout, kr.aout, ea.aout
                    if mois_pointe == '9':
                        et0, kc, kr, ea = et0.sept, kc.sept, kr.sept, ea.sept
                    if mois_pointe == '10':
                        et0, kc, kr, ea = et0.oct, kc.oct, kr.oct, ea.oct
                    if mois_pointe == '11':
                        et0, kc, kr, ea = et0.nov, kc.nov, kr.nov, ea.nov
                    if mois_pointe == '12':
                        et0, kc, kr, ea = et0.dec, kc.dec, kr.dec, ea.dec
                    try:
                        bb = '%.2f' % ((kc * kr * et0) / ea)
                    except:
                        bb = 'NAN'
                    infos.append([cult.name or '-', et0 or '-', kc or '-', kr or '-', ea or '-', bb or '-'])
        return infos

    @api.model
    def create(self, vals):

        vals['num_dossier_report'] = vals['sequence_agric'] = self.env['ir.sequence'].next_by_code('project.project.agricul') or ''

        return super(ProjectProject, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(ProjectProject, self).write(vals)
        for o in self:
            for line in o.amh_region_lines:
                line.onchange_vals_month()
        return res

    # @api.constrains('state')
    # def constrains_state_sequence(self):
    #     for o in self:
    #         if o.state == 'won':
    #             seq = self.env['ir.sequence'].next_by_code('project.project.agricul') or ''
    #             o.sequence_agric = seq + '/' + str(datetime.now().year)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ Override read_group to always display all states. """
        if groupby and groupby[0] == "state":
            # Default result structure
            states = [('new', 'Nouveaux  Dossiers'),
                              ('qalified', "Dossiers en attente d'approbation"),
                              ('won', 'Dossiers approuvés'),
                              ('installed', 'Dossiers installés'),
                              ('lost', 'Dessiers Pérdus')]
            read_group_all_states = [{
                '__context': {'group_by': groupby[1:]},
                '__domain': domain + [('state', '=', state_value)],
                'state': state_value,
                'state_count': 0,
            } for state_value, state_name in states]
            # Get standard results
            read_group_res = super(ProjectProject, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                                    orderby=orderby)
            # Update standard results with default results
            result = []
            for state_value, state_name in states:
                res = filter(lambda x: x['state'] == state_value, read_group_res)
                if not res:
                    res = filter(lambda x: x['state'] == state_value, read_group_all_states)
                if state_value == 'cancel':
                    res[0]['__fold'] = True
                res[0]['state'] = [state_value, state_name]
                result.append(res[0])
            return result
        else:
            return super(ProjectProject, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                          orderby=orderby)

    @api.onchange('amh_region_id')
    def on_change_region(self):
        """Generer le amh_region_lines"""
        for o in self:
            # self._origin
            o_vals = o.copy_data()
            o.update({'amh_region_lines': False})
            if o.amh_region_id:
                to_create = []
                for line in o.amh_region_id.region_lines:
                    to_create.append({
                        'project_id': o.id,
                        'name': line.name if line.name != 'bem3' else 'pemm',
                        'sept': line.sept,
                        'oct': line.oct,
                        'nov': line.nov,
                        'dec': line.dec,
                        'jan': line.jan,
                        'fev': line.fev,
                        'mars': line.mars,
                        'avr': line.avr,
                        'mai': line.mai,
                        'juin': line.juin,
                        'juil': line.juil,
                        'aout': line.aout,
                        'amh_region_id': False,
                    })
                for new_line_values in to_create:
                    created = self.env['amh.region.line'].new(new_line_values)
                    created.project_id = o

    @api.multi
    def generate_synthese(self):
        for o in self:
            o.sytheses_prj.unlink()
            if o.amh_cultures_irg:
                for c in o.amh_cultures_irg:
                    created = self.env['amh.synthese'].create({
                        'culture_irg': c.id,
                        'project_id': o.id,
                    })
                    created.project_id = o
                    created.onchange_fct1()

    @api.multi
    def generate_besoin_eau(self):
        for o in self:
            # o.update({'culture_prj_lines': False})
            o.culture_prj_lines.unlink()
            o.dynm_precalcul_lines.unlink()
            o.dynm_precalcul_down2_lines.unlink()
            to_create = []
            to_create_precalcul = []
            to_create_precalcul_down2 = []
            if o.amh_cultures_irg:
                uniq_clts = [irg.amh_culture_id.id for irg in o.amh_cultures_irg if irg.amh_culture_id]
                uniq_clts = list(set(uniq_clts))
                cultures = self.env['amh.culture'].browse(uniq_clts)
                for cult in cultures:
                    grp_culture = o.amh_cultures_irg.filtered(lambda r: r.amh_culture_id.id == cult.id)
                    tot_superfice = sum([lc.superficie for lc in grp_culture])
                    if True:  # irg.amh_culture_id:
                        for line in cult.culture_lines:
                            to_create.append({
                                'project_id': o.id,
                                'amh_culture_id': False,
                                'amh_culture_prj_id': cult.id,
                                'name': line.name,
                                'sept': line.sept,
                                'oct': line.oct,
                                'nov': line.nov,
                                'dec': line.dec,
                                'jan': line.jan,
                                'fev': line.fev,
                                'mars': line.mars,
                                'avr': line.avr,
                                'mai': line.mai,
                                'juin': line.juin,
                                'juil': line.juil,
                                'aout': line.aout,
                            })
                    for n_prec in NAME_PRECALCUL_CULTURE:
                        to_create_precalcul.append({
                            'project_id': o.id,
                            'amh_culture_id': cult.id,
                            'attribut': n_prec[0],
                            'sept': tot_superfice if n_prec[0] == 'supha' else 0,
                            'oct': tot_superfice if n_prec[0] == 'supha' else 0,
                            'nov': tot_superfice if n_prec[0] == 'supha' else 0,
                            'dec': tot_superfice if n_prec[0] == 'supha' else 0,
                            'jan': tot_superfice if n_prec[0] == 'supha' else 0,
                            'fev': tot_superfice if n_prec[0] == 'supha' else 0,
                            'mars': tot_superfice if n_prec[0] == 'supha' else 0,
                            'avr': tot_superfice if n_prec[0] == 'supha' else 0,
                            'mai': tot_superfice if n_prec[0] == 'supha' else 0,
                            'juin': tot_superfice if n_prec[0] == 'supha' else 0,
                            'juil': tot_superfice if n_prec[0] == 'supha' else 0,
                            'aout': tot_superfice if n_prec[0] == 'supha' else 0,
                        })

                for n_prec in NAME_PRECALCUL_DOWN2:
                    to_create_precalcul_down2.append({
                        'project_id': o.id,
                        'attribut': n_prec[0],
                    })

                for new_line_values in to_create:
                    created = self.env['amh.culture.line'].create(new_line_values)
                    created.project_id = o

                for new_line_values in to_create_precalcul:
                    created = self.env['amh.precalcul.name'].create(new_line_values)
                    created.project_id = o

                for new_line_values in to_create_precalcul_down2:
                    created = self.env['amh.precalcul.down2'].create(new_line_values)
                    created.project_id = o
                o.resource_eau_dispo = sum([pui.debit_exploit for pui in o.amh_puit_ids])

    @api.multi
    def update_besoin_eau(self):
        for o in self:
            # Resource en eau disponible
            rs_eau = sum([pui.debit_exploit for pui in o.amh_puit_ids])
            o.update({
                'resource_eau_dispo': rs_eau,
            })
            # Update Precalcul lines
            for ldyn in o.dynm_precalcul_lines:
                for lc in o.culture_prj_lines:
                    if ldyn.amh_culture_id.id == lc.amh_culture_prj_id.id:
                        if ldyn.attribut == lc.name == 'kc':
                            ldyn.update({
                                'sept': lc.sept,
                                'oct': lc.oct,
                                'nov': lc.nov,
                                'dec': lc.dec,
                                'jan': lc.jan,
                                'fev': lc.fev,
                                'mars': lc.mars,
                                'avr': lc.avr,
                                'mai': lc.mai,
                                'juin': lc.juin,
                                'juil': lc.juil,
                                'aout': lc.aout,
                            })
                        if ldyn.attribut == lc.name in 'kr':
                            if ldyn.sept <= 0:
                                ldyn.update({
                                    'sept': lc.sept,
                                    'oct': lc.oct,
                                    'nov': lc.nov,
                                    'dec': lc.dec,
                                    'jan': lc.jan,
                                    'fev': lc.fev,
                                    'mars': lc.mars,
                                    'avr': lc.avr,
                                    'mai': lc.mai,
                                    'juin': lc.juin,
                                    'juil': lc.juil,
                                    'aout': lc.aout,
                                })
                            else:
                                ldyn.update({
                                    'oct': ldyn.sept,
                                    'nov': ldyn.sept,
                                    'dec': ldyn.sept,
                                    'jan': ldyn.sept,
                                    'fev': ldyn.sept,
                                    'mars': ldyn.sept,
                                    'avr': ldyn.sept,
                                    'mai': ldyn.sept,
                                    'juin': ldyn.sept,
                                    'juil': ldyn.sept,
                                    'aout': ldyn.sept,
                                })
                        if ldyn.attribut == lc.name in 'ea':
                            ldyn.update({
                                'sept': lc.sept,
                                'oct': lc.oct,
                                'nov': lc.nov,
                                'dec': lc.dec,
                                'jan': lc.jan,
                                'fev': lc.fev,
                                'mars': lc.mars,
                                'avr': lc.avr,
                                'mai': lc.mai,
                                'juin': lc.juin,
                                'juil': lc.juil,
                                'aout': lc.aout,
                            })
                # calcul BE(m3)06
                if ldyn.attribut == 'be':
                    et0_l = o.amh_region_lines.filtered(lambda r: r.name == 'et0mmmois')
                    kc_kr_supha = o.dynm_precalcul_lines.filtered(lambda r: r.attribut in ['kc', 'kr', 'supha'] and (
                            r.amh_culture_id.id == ldyn.amh_culture_id.id))
                    ea = o.dynm_precalcul_lines.filtered(lambda r: r.attribut == 'ea' and (
                            r.amh_culture_id.id == ldyn.amh_culture_id.id))
                    if et0_l and len(kc_kr_supha) >= 3 and ea:
                        if ea[0] == 0:
                            raise ValidationError("EA est null, devision par 0 ets impossible")
                    else:
                        raise ValidationError("Des données sont manquantes")

                    def multip(sequec):
                        p = 1
                        for s in sequec:
                            p *= s
                        return p

                    ldyn.update({
                        'sept': (et0_l[0].sept * multip([r.sept for r in kc_kr_supha]) * 10) / ea[0].sept,
                        'oct': (et0_l[0].oct * multip([r.oct for r in kc_kr_supha]) * 10) / ea[0].oct,
                        'nov': (et0_l[0].nov * multip([r.nov for r in kc_kr_supha]) * 10) / ea[0].nov,
                        'dec': (et0_l[0].dec * multip([r.dec for r in kc_kr_supha]) * 10) / ea[0].dec,
                        'jan': (et0_l[0].jan * multip([r.jan for r in kc_kr_supha]) * 10) / ea[0].jan,
                        'fev': (et0_l[0].fev * multip([r.fev for r in kc_kr_supha]) * 10) / ea[0].fev,
                        'mars': (et0_l[0].mars * multip([r.mars for r in kc_kr_supha]) * 10) / ea[0].mars,
                        'avr': (et0_l[0].avr * multip([r.avr for r in kc_kr_supha]) * 10) / ea[0].avr,
                        'mai': (et0_l[0].mai * multip([r.mai for r in kc_kr_supha]) * 10) / ea[0].mai,
                        'juin': (et0_l[0].juin * multip([r.juin for r in kc_kr_supha]) * 10) / ea[0].juin,
                        'juil': (et0_l[0].juil * multip([r.juil for r in kc_kr_supha]) * 10) / ea[0].juil,
                        'aout': (et0_l[0].aout * multip([r.aout for r in kc_kr_supha]) * 10) / ea[0].aout,
                    })

            # calcul btc_cultres
            for line in o.dynm_precalcul_lines:
                if line.attribut == 'btc_cult':
                    clt_id = line.amh_culture_id and line.amh_culture_id.id or False
                    if clt_id:
                        pe = o.amh_region_lines.filtered(lambda r: r.name == 'pemm')[0]
                        be = \
                            o.dynm_precalcul_lines.filtered(
                                lambda r: r.attribut == 'be' and r.amh_culture_id.id == clt_id)[
                                0]
                        supha = o.dynm_precalcul_lines.filtered(
                            lambda r: r.attribut == 'supha' and r.amh_culture_id.id == clt_id)[0]
                        line.update({
                            'sept': 0 if (be.sept == 0 or (be.sept <= (pe.sept * 10 * supha.sept))) else (
                                    be.sept - (pe.sept * 10 * supha.sept)),
                            'oct': 0 if (be.oct == 0 or (be.oct <= (pe.oct * 10 * supha.oct))) else (
                                    be.oct - (pe.oct * 10 * supha.oct)),
                            'nov': 0 if (be.nov == 0 or (be.nov <= (pe.nov * 10 * supha.nov))) else (
                                    be.nov - (pe.nov * 10 * supha.nov)),
                            'dec': 0 if (be.dec == 0 or (be.dec <= (pe.dec * 10 * supha.dec))) else (
                                    be.dec - (pe.dec * 10 * supha.dec)),
                            'jan': 0 if (be.jan == 0 or (be.jan <= (pe.jan * 10 * supha.jan))) else (
                                    be.jan - (pe.jan * 10 * supha.jan)),
                            'fev': 0 if (be.fev == 0 or (be.fev <= (pe.fev * 10 * supha.fev))) else (
                                    be.fev - (pe.fev * 10 * supha.fev)),
                            'mars': 0 if (be.mars == 0 or (be.mars <= (pe.mars * 10 * supha.mars))) else (
                                    be.mars - (pe.mars * 10 * supha.mars)),
                            'avr': 0 if (be.avr == 0 or (be.avr <= (pe.avr * 10 * supha.avr))) else (
                                    be.avr - (pe.avr * 10 * supha.avr)),
                            'mai': 0 if (be.mai == 0 or (be.mai <= (pe.mai * 10 * supha.mai))) else (
                                    be.mai - (pe.mai * 10 * supha.mai)),
                            'juin': 0 if (be.juin == 0 or (be.juin <= (pe.juin * 10 * supha.juin))) else (
                                    be.juin - (pe.juin * 10 * supha.juin)),
                            'juil': 0 if (be.juil == 0 or (be.juil <= (pe.juil * 10 * supha.juil))) else (
                                    be.juil - (pe.juil * 10 * supha.juil)),
                            'aout': 0 if (be.aout == 0 or (be.aout <= (pe.aout * 10 * supha.aout))) else (
                                    be.aout - (pe.aout * 10 * supha.aout)),
                        })

            # Precalcules Down2
            for line in o.dynm_precalcul_down2_lines:
                if line.attribut == 'btc':
                    tots = o.dynm_precalcul_lines.filtered(lambda r: r.attribut == 'btc_cult')
                    line.update({
                        'sept': sum([p.sept for p in tots]),
                        'oct': sum([p.oct for p in tots]),
                        'nov': sum([p.nov for p in tots]),
                        'dec': sum([p.dec for p in tots]),
                        'jan': sum([p.jan for p in tots]),
                        'fev': sum([p.fev for p in tots]),
                        'mars': sum([p.mars for p in tots]),
                        'avr': sum([p.avr for p in tots]),
                        'mai': sum([p.mai for p in tots]),
                        'juin': sum([p.juin for p in tots]),
                        'juil': sum([p.juil for p in tots]),
                        'aout': sum([p.aout for p in tots]),
                    })

                if line.attribut == 'dexploi':
                    line.update({
                        'sept': o.resource_eau_dispo,
                        'oct': o.resource_eau_dispo,
                        'nov': o.resource_eau_dispo,
                        'dec': o.resource_eau_dispo,
                        'jan': o.resource_eau_dispo,
                        'fev': o.resource_eau_dispo,
                        'mars': o.resource_eau_dispo,
                        'avr': o.resource_eau_dispo,
                        'mai': o.resource_eau_dispo,
                        'juin': o.resource_eau_dispo,
                        'juil': o.resource_eau_dispo,
                        'aout': o.resource_eau_dispo,
                    })

                if line.attribut == 'nbh':
                    btc_line = o.dynm_precalcul_down2_lines.filtered(lambda r: r.attribut == 'btc')
                    exploi_line = o.dynm_precalcul_down2_lines.filtered(lambda r: r.attribut == 'dexploi')
                    nb_mois_jours = 26
                    if not o.conserver_cal:
                        try:
                            line.update({
                                'sept': btc_line.sept / (exploi_line.sept * nb_mois_jours),
                                'oct': btc_line.oct / (exploi_line.oct * nb_mois_jours),
                                'nov': btc_line.nov / (exploi_line.nov * nb_mois_jours),
                                'dec': btc_line.dec / (exploi_line.dec * nb_mois_jours),
                                'jan': btc_line.jan / (exploi_line.jan * nb_mois_jours),
                                'fev': btc_line.fev / (exploi_line.fev * nb_mois_jours),
                                'mars': btc_line.mars / (exploi_line.mars * nb_mois_jours),
                                'avr': btc_line.avr / (exploi_line.avr * nb_mois_jours),
                                'mai': btc_line.mai / (exploi_line.mai * nb_mois_jours),
                                'juin': btc_line.juin / (exploi_line.juin * nb_mois_jours),
                                'juil': btc_line.juil / (exploi_line.juil * nb_mois_jours),
                                'aout': btc_line.aout / (exploi_line.aout * nb_mois_jours),
                            })
                        except Exception as e:
                            raise ValidationError("En calcule de Nbre d'heures de fonct./jour, dévision par 0")

                if line.attribut == 'vold':
                    nbh_line = o.dynm_precalcul_down2_lines.filtered(lambda r: r.attribut == 'nbh')
                    exploi_line = o.dynm_precalcul_down2_lines.filtered(lambda r: r.attribut == 'dexploi')
                    nb_mois_jours = 26

                    line.update({
                        'sept': (nbh_line.sept * exploi_line.sept * nb_mois_jours),
                        'oct': (nbh_line.oct * exploi_line.oct * nb_mois_jours),
                        'nov': (nbh_line.nov * exploi_line.nov * nb_mois_jours),
                        'dec': (nbh_line.dec * exploi_line.dec * nb_mois_jours),
                        'jan': (nbh_line.jan * exploi_line.jan * nb_mois_jours),
                        'fev': (nbh_line.fev * exploi_line.fev * nb_mois_jours),
                        'mars': (nbh_line.mars * exploi_line.mars * nb_mois_jours),
                        'avr': (nbh_line.avr * exploi_line.avr * nb_mois_jours),
                        'mai': (nbh_line.mai * exploi_line.mai * nb_mois_jours),
                        'juin': (nbh_line.juin * exploi_line.juin * nb_mois_jours),
                        'juil': (nbh_line.juil * exploi_line.juil * nb_mois_jours),
                        'aout': (nbh_line.aout * exploi_line.aout * nb_mois_jours),
                    })
                if line.attribut == 'bilanrb':
                    bct_line = o.dynm_precalcul_down2_lines.filtered(lambda r: r.attribut == 'btc')
                    vold_line = o.dynm_precalcul_down2_lines.filtered(lambda r: r.attribut == 'vold')
                    line.update({
                        'sept': vold_line.sept - bct_line.sept,
                        'oct': vold_line.oct - bct_line.oct,
                        'nov': vold_line.nov - bct_line.nov,
                        'dec': vold_line.dec - bct_line.dec,
                        'jan': vold_line.jan - bct_line.jan,
                        'fev': vold_line.fev - bct_line.fev,
                        'mars': vold_line.mars - bct_line.mars,
                        'avr': vold_line.avr - bct_line.avr,
                        'mai': vold_line.mai - bct_line.mai,
                        'juin': vold_line.juin - bct_line.juin,
                        'juil': vold_line.juil - bct_line.juil,
                        'aout': vold_line.aout - bct_line.aout,
                    })
                # if line.attribut == 'volmp':
                #     line.update({
                #         'oct': line.sept,
                #         'nov': line.sept,
                #         'dec': line.sept,
                #         'jan': line.sept,
                #         'fev': line.sept,
                #         'mars': line.sept,
                #         'avr': line.sept,
                #         'mai': line.sept,
                #         'juin': line.sept,
                #         'juil': line.sept,
                #         'aout': line.sept,
                #     })
                if line.attribut == 'bilanrbb':
                    vold_line = o.dynm_precalcul_down2_lines.filtered(lambda r: r.attribut == 'vold')  # C22
                    voldmp_line = o.dynm_precalcul_down2_lines.filtered(lambda r: r.attribut == 'volmp')  # C24
                    bct_line = o.dynm_precalcul_down2_lines.filtered(lambda r: r.attribut == 'btc')  # C18

                    voldmp_line.update({'sept': 0})
                    prec = (vold_line.sept + 0) - bct_line.sept
                    line.update({'sept': prec})

                    voldmp_line.update({'oct': prec})
                    prec = (vold_line.oct + prec) - bct_line.oct
                    line.update({'oct': prec})

                    voldmp_line.update({'nov': prec})
                    prec = (vold_line.nov + prec) - bct_line.nov
                    line.update({'nov': prec})

                    voldmp_line.update({'dec': prec})
                    prec = (vold_line.dec + prec) - bct_line.dec
                    line.update({'dec': prec})

                    voldmp_line.update({'jan': prec})
                    prec = (vold_line.jan + prec) - bct_line.jan
                    line.update({'jan': prec})

                    voldmp_line.update({'fev': prec})
                    prec = (vold_line.fev + prec) - bct_line.fev
                    line.update({'fev': prec})

                    voldmp_line.update({'mars': prec})
                    prec = (vold_line.mars + prec) - bct_line.mars
                    line.update({'mars': prec})

                    voldmp_line.update({'avr': prec})
                    prec = (vold_line.avr + prec) - bct_line.avr
                    line.update({'avr': prec})

                    voldmp_line.update({'mai': prec})
                    prec = (vold_line.mai + prec) - bct_line.mai
                    line.update({'mai': prec})

                    voldmp_line.update({'juin': prec})
                    prec = (vold_line.juin + prec) - bct_line.juin
                    line.update({'juin': prec})

                    voldmp_line.update({'juil': prec})
                    prec = (vold_line.juil + prec) - bct_line.juil
                    line.update({'juil': prec})

                    voldmp_line.update({'aout': prec})
                    prec = (vold_line.aout + prec) - bct_line.aout
                    line.update({'aout': prec})

                    # line.update({
                    #     'sept': (vold_line.sept + voldmp_line.sept) - bct_line.sept,
                    #     'oct': (vold_line.oct + voldmp_line.oct) - bct_line.oct,
                    #     'nov': (vold_line.nov + voldmp_line.nov) - bct_line.nov,
                    #     'dec': (vold_line.dec + voldmp_line.dec) - bct_line.dec,
                    #     'jan': (vold_line.jan + voldmp_line.jan) - bct_line.jan,
                    #     'fev': (vold_line.fev + voldmp_line.fev) - bct_line.fev,
                    #     'mars': (vold_line.mars + voldmp_line.mars) - bct_line.mars,
                    #     'avr': (vold_line.avr + voldmp_line.avr) - bct_line.avr,
                    #     'mai': (vold_line.mai + voldmp_line.mai) - bct_line.mai,
                    #     'juin': (vold_line.juin + voldmp_line.juin) - bct_line.juin,
                    #     'juil': (vold_line.juil + voldmp_line.juil) - bct_line.juil,
                    #     'aout': (vold_line.aout + voldmp_line.aout) - bct_line.aout,
                    # })


class CultureIrriguer(models.Model):
    _name = 'amh.culture.irriguer'

    @api.depends('densite_x', 'densite_y', 'amh_culture_id')
    def _compute_name(self):
        for o in self:
            o.name = (o.amh_culture_id.name or '') + ' ' + (o.densite_str)

    name = fields.Char('Nom', compute='_compute_name')
    amh_culture_id = fields.Many2one('amh.culture', string="Culture", required=True, ondelete='cascade')
    project_id = fields.Many2one('project.project', string="Projet", required=False, ondelete='cascade')
    superficie = fields.Float("Superficie en (ha)", required=True, help="Superfice decimal", digits=(14, 5))
    observation = fields.Float("Observations", required=True)
    observation_unit = fields.Char("", default="Goutt/arbre")
    densite_x = fields.Float("Densité x", required=True)
    densite_y = fields.Float("Densité y", required=True)
    densite_str = fields.Char("Densité", compute='_compute_strs')
    observation_str = fields.Char("Observations", compute='_compute_strs')
    superficie_str = fields.Char("Superficie (ha) ", required=True, help="Sperficie exemple 1ha 00A 50CA")

    @api.depends('densite_x', 'densite_y', 'observation', 'observation_unit')
    def _compute_strs(self):
        for o in self:
            obser = int(o.observation or 0)
            obser = (str(obser) + ' ') if obser else ''
            o.observation_str = obser + str(o.observation_unit or '')
            o.densite_str = '(' + str(o.densite_x or '0') + 'X' + str(o.densite_y or '0') + ')' + 'm'

    @api.onchange('superficie')
    def formule_superfice(self):
        for o in self:
            if o.superficie:
                x = int((round(o.superficie or 0, 5) * 10000))
                ha = int(float(x) / 10000)
                reste = x - (ha * 10000)
                a = int(reste / 100)
                reste = reste - (a * 100)
                ca = int(reste)
                o.superficie_str = "{} ha {} a {} ca".format(str(ha), str(a).zfill(2), str(ca).zfill(2)[:2])


class Puits(models.Model):
    _name = 'amh.puits'

    def get_default_type(self):
        return self.env.ref('agricul_core.puit_default_type').id

    project_id = fields.Many2one('project.project', string="Projet", required=False, ondelete='cascade')
    description = fields.Text(string="Description")
    prof_tot = fields.Float("Profondeur totale (m)", required=True)
    niv_hedrostat = fields.Float("Niveau hydrostatique (m)", required=True)
    niv_hedrodynm = fields.Float("Niveau hydrodynamique (m)", required=True)
    debit_exploit = fields.Float("Débit d'exploitation (m3/h)", required=True)
    debit_exploit_ls = fields.Float("Débit d'exploitation l/s", compute='_computed_fields')
    pression_service_mce = fields.Float("Pression de service (mCE)", required=False)
    qualit_eau = fields.Char(string="Qualité de l'eau")
    puit_type_id = fields.Many2one('amh.puits.type', string="Type", required=True, default=get_default_type)

    @api.depends('debit_exploit')
    def _computed_fields(self):
        for o in self:
            o.debit_exploit_ls = float((o.debit_exploit or 0)) / 3.6


class PuitsType(models.Model):
    _name = 'amh.puits.type'

    name = fields.Char('Designation', required=True)


class LignePrecalcul(models.Model):
    _name = 'amh.precalcul.name'

    project_id = fields.Many2one('project.project', string="Projet", required=False, ondelete='cascade')
    amh_culture_id = fields.Many2one('amh.culture', string="Culture", required=False)

    attribut = fields.Selection(NAME_PRECALCUL_CULTURE, string='Attribut')
    sept = fields.Float(string="Sept.", )
    oct = fields.Float(string="Oct.")
    nov = fields.Float(string="Nov.")
    dec = fields.Float(string="Déc.")
    jan = fields.Float(string="Jan.")
    fev = fields.Float(string="Fev.")
    mars = fields.Float(string="Mars")
    avr = fields.Float(string="Avr.")
    mai = fields.Float(string="Mai")
    juin = fields.Float(string="Juin")
    juil = fields.Float(string="Jui.")
    aout = fields.Float(string="Août.")

    type_stat = fields.Boolean(string='Down or top in precacul', default=True)
    link_line = fields.Many2one('amh.precalcul.name', string="this is top")

    # link_line_ids = fields.One2many('amh.precalcul.name', string="links, change parent change thsi")

    total = fields.Float('Total', compute='compute_total_line')
    maxval = fields.Float('Total', compute='compute_total_line')

    @api.multi
    def compute_total_line(self):
        for o in self:
            o.total = o.sept + o.oct + o.nov + o.dec + o.jan + o.fev + o.mars + o.avr + o.mai + o.juin + o.juil + o.aout
            o.maxval = max([o.sept, o.oct, o.nov, o.dec, o.jan, o.fev, o.mars, o.avr, o.mai, o.juin, o.juil, o.aout])
    # @api.multi
    # def write(self, vals):
    #     res = super(LignePrecalcul, self).write(vals)
    #     for o in self:
    #         if vals.get('sept'):
    #             if o.link_line:
    #                 o.link_line.sept = o.sept
    #         if vals.get('oct'):
    #             if o.link_line:
    #                 o.link_line.oct = o.oct
    #         if vals.get('nov'):
    #             if o.link_line:
    #                 o.link_line.sept = o.sept
    #         if vals.get('dec'):
    #             if o.link_line:
    #                 o.link_line.dec = o.dec
    #         if vals.get('jan'):
    #             if o.link_line:
    #                 o.link_line.jan = o.jan
    #         if vals.get('fev'):
    #             if o.link_line:
    #                 o.link_line.fev = o.fev
    #         if vals.get('mars'):
    #             if o.link_line:
    #                 o.link_line.mars = o.mars
    #         if vals.get('avr'):
    #             if o.link_line:
    #                 o.link_line.avr = o.avr
    #         if vals.get('mai'):
    #             if o.link_line:
    #                 o.link_line.mai = o.mai
    #         if vals.get('juin'):
    #             if o.link_line:
    #                 o.link_line.juin = o.juin
    #         if vals.get('juil'):
    #             if o.link_line:
    #                 o.link_line.juil = o.juil
    #         if vals.get('aout'):
    #             if o.link_line:
    #                 o.link_line.aout = o.aout


class LignePrecalculDown2(models.Model):
    _name = 'amh.precalcul.down2'

    project_id = fields.Many2one('project.project', string="Projet", required=False, ondelete='cascade')

    attribut = fields.Selection(NAME_PRECALCUL_DOWN2, string='Attribut')
    sept = fields.Float(string="Sept.")
    oct = fields.Float(string="Oct.")
    nov = fields.Float(string="Nov.")
    dec = fields.Float(string="Déc.")
    jan = fields.Float(string="Jan.")
    fev = fields.Float(string="Fev.")
    mars = fields.Float(string="Mars")
    avr = fields.Float(string="Avr.")
    mai = fields.Float(string="Mai")
    juin = fields.Float(string="Juin")
    juil = fields.Float(string="Jui.")
    aout = fields.Float(string="Août.")
    total = fields.Float('Total', compute='compute_total_line')
    maxval = fields.Float('Total', compute='compute_total_line')

    @api.multi
    def compute_total_line(self):
        for o in self:
            o.total = o.sept + o.oct + o.nov + o.dec + o.jan + o.fev + o.mars + o.avr + o.mai + o.juin + o.juil + o.aout
            o.maxval = max([o.sept, o.oct, o.nov, o.dec, o.jan, o.fev, o.mars, o.avr, o.mai, o.juin, o.juil, o.aout])
            if o.attribut == 'bilanrbb' and o.project_id:
                vold_line = o.project_id.dynm_precalcul_down2_lines.filtered(lambda r: r.attribut == 'vold')  # C22
                bct_line = o.project_id.dynm_precalcul_down2_lines.filtered(lambda r: r.attribut == 'btc')  # C18
                #print("===",vold_line,bct_line)
                #print((vold_line.total - bct_line.total) if (vold_line and  bct_line) else 0)
                o.total = (vold_line.total - bct_line.total) if (vold_line and  bct_line) else 0