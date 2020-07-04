# -*- coding: utf-8 -*-

import time
import math

from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class SpecialitePartner(models.Model):
    _name = "avad.medcin.specialite"

    name = fields.Char(string="Nom", required=True)

class ResPartnerAMh(models.Model):
    _inherit = "res.partner"# -*- coding: utf-8 -*-

import time
import math

from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class SpecialitePartner(models.Model):
    _name = "avad.medcin.specialite"

    name = fields.Char(string="Nom", required=True)

class ResPartnerAMh(models.Model):
    _inherit = "res.partner"

    @api.depends('poids', 'taille')
    def _compute_imc(self):
        for o in self:
            o.imc = (float(o.poids) / float(o.taille ** 2)) if (o.taille and o.poids) else 0

    type_client = fields.Selection(
        (('autre', 'Autre'), ('patient', 'Patient'), ('medecins', 'Médecin'), ('institution', 'Institution')),
        string='Type client', default='autre', required=True)
    cin = fields.Char(string="CIN")
    genre = fields.Selection([('Mr.', 'Mr.'), ('Mme.', 'Mme.'), ('Mlle.', 'Mlle.')], string='Genre', required=False)
    num_national_medeci = fields.Char(string='Code Médecin (INP)')
    ref2 = fields.Char('Ref. client', size=64)
    is_company = fields.Boolean(string='Is a Company', default=False,
                                help="Check if the contact is a company, otherwise it is a person")
    specialite = fields.Many2one("avad.medcin.specialite", "Spécialité")
    civilite = fields.Selection([('professor', 'Professeur'), ('doctor', 'Docteur')], string='Civilité', required=False)

    ddn = fields.Date('Date de naissance')

    @api.depends('poids', 'taille')
    def _compute_imc(self):
        for o in self:
            o.imc = (float(o.poids) / float(o.taille ** 2)) if (o.taille and o.poids) else 0

    type_client = fields.Selection(
        (('autre', 'Autre'), ('patient', 'Patient'), ('medecins', 'Médecin'), ('institution', 'Institution')),
        string='Type client', default='autre', required=True)
    cin = fields.Char(string="CIN")
    genre = fields.Selection([('Mr.', 'Mr.'), ('Mme.', 'Mme.'), ('Mlle.', 'Mlle.')], string='Genre', required=False)
    num_national_medeci = fields.Char(string='Code Médecin (INP)')
    ref2 = fields.Char('Ref. client', size=64)
    is_company = fields.Boolean(string='Is a Company', default=False,
                                help="Check if the contact is a company, otherwise it is a person")
    specialite = fields.Many2one("avad.medcin.specialite", "Spécialité")
    civilite = fields.Selection([('professor', 'Professeur'), ('doctor', 'Docteur')], string='Civilité', required=False)

    ddn = fields.Date('Date de naissance')
    iah_initial = fields.Integer("IAH Initial")
    poids = fields.Float("Poids (kg)")
    taille = fields.Float("Taille (m)")
    imc = fields.Float("IMC", compute=_compute_imc)
    cost_logistique = fields.Float("Cout logistique")



    @api.model
    def create(self, values):
        res = super(ResPartnerAMh, self).create(values)
        for o in res:
            if not o.ref2:
                try:
                    o.ref2 = self.env['ir.sequence'].next_by_code('res.partner.avad.seq1') or False
                except:
                    raise ValidationError("Le sequence code = 'res.partner.avad.seq1' n'existe pas dans la base.")
        return res

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if not default:
            default = {}
        default['ref2'] = False
        res = super(ResPartnerAMh, self).copy(default=default)
        return res
