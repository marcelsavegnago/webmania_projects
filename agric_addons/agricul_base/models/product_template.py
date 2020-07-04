# -*- coding: utf-8 -*-

import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

# class GoutteurTypeAMh(models.Model):
#     _name = "goutteur.type"
#
#     name = fields.Char("Designation", compute='_compute_name_tg')
#     designation = fields.Char("Nom", required=True)
#     dims = fields.Float(" (L)", required=True)
#
#     @api.depends('designation','dims')
#     def _compute_name_tg(self):
#         for o in self:
#             o.name = (o.designation or '')+' '+(str(o.dims)+'L' or '')

class ProductCateg(models.Model):
     _inherit = "product.category"

     type_amh = fields.Selection([('goutteurs','Goutteurs'),
                                  ('gaines','Gaines'),
                                  ('pvc','PVC')
                                 , ('pehd', 'PEHD'),
                                  ('pebd','PEBD'),
                                  ('woltman','Woltman)')], default=False)

class ProductTemplateAMh(models.Model):
    _inherit = "product.template"

    type_article = fields.Char("Type article (Amh)", compute= '_compute_type_article', store=True)
    #goutteur_type = fields.Many2one('goutteur.type', string= "Type de goutteur",required=False)
    goutteur_type = fields.Selection([('boutton','BOUTTON'), ('integre','INTEGRE')],
                                     string='Type de goutteur')
    q_moyen = fields.Float(string="Q moyen (l/h)", required=False)
    exposant = fields.Float(string="Exposant (x)", required=False)
    k_value = fields.Float(string="K", required=False)
    validate_date = fields.Date(string="Date de validité", required=False)
    longeur_qte = fields.Float(string='LONGUEUR /qte paquet', required=False)
    pression_service = fields.Float(string='Pression  de service du distributeur')
    goutteur_sans_essai = fields.Boolean(string="Goutteur sans bultin d'essai", default=False)
    excrt_gtr = fields.Float(string="Ecartement entre goutteurs")

    #pvc:1, PEHD / PEBD:2  fields
    mesure = fields.Float(string='Diametre Normalisé')#1
    type_jn_cl = fields.Selection([('joint','A joint'),('coller','A coller')], default='joint', string='Type (A joint / a coller)')  #1
    diametre_ext = fields.Float(string='Diametre Mesuré')#1,2
    diametre_int = fields.Float(string='Epaisseur Normalisé')#1,2
    diametre_int2 = fields.Float(string='Epaisseur Mesuré')  # 1,2
    debit_max = fields.Float(string='Débit max  (m³/h)')#1,2
    vitesse_max = fields.Float(string='Vitess max')#1,2
    pression = fields.Float(string='Pression (10 / 15)')#2

    #woltman category
    dn_mm = fields.Float(string="DN (mm)")
    debits_wm = fields.Char(string="Debits")
    #debit_woltman_qmin = fields.Float(string="Qmin (m3/h)")
    #debit_woltman_qt = fields.Float(string="Qt (m3/h)")
    #debit_woltman_qn = fields.Float(string="Qn (m3/h)")
    #debit_woltman_qmax = fields.Float(string="Qmax (m3/h)")

    @api.depends('categ_id')
    def _compute_type_article(self):
        for o in self:
            o.type_article = o.categ_id.type_amh if o.categ_id else False
