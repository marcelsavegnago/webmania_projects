# -*- coding: utf-8 -*-

import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

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

NAME_LINES_REGION = [('et0mmjr', 'ET0 (mm/jour)'),
                     ('et0mmmois', 'ET0 (mm/mois)'),
                     ('et0m3mois', 'ET0 (m3/mois)'),
                     ('bem3', 'Pe (mm/mois)'), ]
NAME_LINES_CULTURE = [('kc', 'Kc'), ('kr', 'Kr'), ('ea', 'Ea'), ]
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


class RegionAMH(models.Model):
    _name = 'amh.region'

    @api.multi
    @api.onchange('name')
    def get_default_get_lines(self):
        lines = self.env['amh.region.line']
        for o in self:
            if len(o.region_lines):
                continue
            for l in NAME_LINES_REGION:
                line = lines.new({
                    'amh_region_id': o.id,
                    'name': l[0],
                })
                line.amh_region_id = o

    name = fields.Char("Nom", required=True)
    region_lines = fields.One2many('amh.region.line', 'amh_region_id', string="Mois")

    @api.model
    def create(self, vals):
        res = super(RegionAMH, self).create(vals)
        res.get_default_get_lines()
        return res

    @api.multi
    def write(self, vals):
        res = super(RegionAMH, self).write(vals)
        for o in self:
            for line in o.region_lines:
                line.onchange_vals_month()
        return res


class ResgionLineAMH(models.Model):
    _name = 'amh.region.line'

    amh_region_id = fields.Many2one('amh.region', string="Région", required=False, ondelete='cascade')
    project_id = fields.Many2one('project.project', string="Projet", required=False, ondelete='cascade')

    name = fields.Selection(NAME_LINES_REGION+[('pemm','Pe(mm/mois)')], string='Attribut')
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

    @api.multi
    def compute_total_line(self):
        for o in self:
            o.total = o.sept + o.oct + o.nov + o.dec + o.jan + o.fev + o.mars + o.avr + o.mai + o.juin + o.juil + o.aout

    @api.multi
    @api.onchange('sept', 'oct', 'nov', 'dec', 'jan', 'fev', 'mars', 'avr', 'mai', 'juin', 'juil', 'aout')
    def onchange_vals_month(self):
        for o in self:
            if o.name and o.name == 'et0mmjr':
                if o.amh_region_id:
                    for line in o.amh_region_id.region_lines:
                        if line.name == 'et0mmmois':
                            line.sept = MONTH_DAYS["9"] * o.sept
                            line.oct = MONTH_DAYS["10"] * o.oct
                            line.nov = MONTH_DAYS["11"] * o.nov
                            line.dec = MONTH_DAYS["12"] * o.dec
                            line.jan = MONTH_DAYS["1"] * o.jan
                            line.fev = MONTH_DAYS["2"] * o.fev
                            line.mars = MONTH_DAYS["3"] * o.mars
                            line.avr = MONTH_DAYS["4"] * o.avr
                            line.mai = MONTH_DAYS["5"] * o.mai
                            line.juin = MONTH_DAYS["6"] * o.juin
                            line.juil = MONTH_DAYS["7"] * o.juil
                            line.aout = MONTH_DAYS["8"] * o.aout
                        if line.name == 'et0m3mois':
                            line.sept = MONTH_DAYS["9"] * o.sept * 10
                            line.oct = MONTH_DAYS["10"] * o.oct * 10
                            line.nov = MONTH_DAYS["11"] * o.nov * 10
                            line.dec = MONTH_DAYS["12"] * o.dec * 10
                            line.jan = MONTH_DAYS["1"] * o.jan * 10
                            line.fev = MONTH_DAYS["2"] * o.fev * 10
                            line.mars = MONTH_DAYS["3"] * o.mars * 10
                            line.avr = MONTH_DAYS["4"] * o.avr * 10
                            line.mai = MONTH_DAYS["5"] * o.mai * 10
                            line.juin = MONTH_DAYS["6"] * o.juin * 10
                            line.juil = MONTH_DAYS["7"] * o.juil * 10
                            line.aout = MONTH_DAYS["8"] * o.aout * 10
                if o.project_id:
                    for line in o.project_id.amh_region_lines:
                        if line.name == 'et0mmmois':
                            line.sept = MONTH_DAYS["9"] * o.sept
                            line.oct = MONTH_DAYS["10"] * o.oct
                            line.nov = MONTH_DAYS["11"] * o.nov
                            line.dec = MONTH_DAYS["12"] * o.dec
                            line.jan = MONTH_DAYS["1"] * o.jan
                            line.fev = MONTH_DAYS["2"] * o.fev
                            line.mars = MONTH_DAYS["3"] * o.mars
                            line.avr = MONTH_DAYS["4"] * o.avr
                            line.mai = MONTH_DAYS["5"] * o.mai
                            line.juin = MONTH_DAYS["6"] * o.juin
                            line.juil = MONTH_DAYS["7"] * o.juil
                            line.aout = MONTH_DAYS["8"] * o.aout
                        if line.name == 'et0m3mois':
                            line.sept = MONTH_DAYS["9"] * o.sept * 10
                            line.oct = MONTH_DAYS["10"] * o.oct * 10
                            line.nov = MONTH_DAYS["11"] * o.nov * 10
                            line.dec = MONTH_DAYS["12"] * o.dec * 10
                            line.jan = MONTH_DAYS["1"] * o.jan * 10
                            line.fev = MONTH_DAYS["2"] * o.fev * 10
                            line.mars = MONTH_DAYS["3"] * o.mars * 10
                            line.avr = MONTH_DAYS["4"] * o.avr * 10
                            line.mai = MONTH_DAYS["5"] * o.mai * 10
                            line.juin = MONTH_DAYS["6"] * o.juin * 10
                            line.juil = MONTH_DAYS["7"] * o.juil * 10
                            line.aout = MONTH_DAYS["8"] * o.aout * 10


# -------------- Culture ----

class CultureAMH(models.Model):
    _name = 'amh.culture'

    @api.multi
    @api.onchange('name')
    def get_default_get_lines(self):
        lines = self.env['amh.culture.line']
        for o in self:
            if len(o.culture_lines):
                continue
            for l in NAME_LINES_CULTURE:
                line = lines.new({
                    'amh_culture_id': o.id,
                    'name': l[0],
                    'sept': 0 if l[0] != 'ea' else 0.9,
                    'oct': 0 if l[0] != 'ea' else 0.9,
                    'nov': 0 if l[0] != 'ea' else 0.9,
                    'dec': 0 if l[0] != 'ea' else 0.9,
                    'jan': 0 if l[0] != 'ea' else 0.9,
                    'fev': 0 if l[0] != 'ea' else 0.9,
                    'mars': 0 if l[0] != 'ea' else 0.9,
                    'avr': 0 if l[0] != 'ea' else 0.9,
                    'mai': 0 if l[0] != 'ea' else 0.9,
                    'juin': 0 if l[0] != 'ea' else 0.9,
                    'juil': 0 if l[0] != 'ea' else 0.9,
                    'aout': 0 if l[0] != 'ea' else 0.9,
                })
                line.amh_culture_id = o

    name = fields.Char("Nom", required=True)
    culture_lines = fields.One2many('amh.culture.line', 'amh_culture_id', string="Mois")

    # amh_region_id = fields.Many2one('amh.region', string='Région', required=True)

    @api.model
    def create(self, vals):
        res = super(CultureAMH, self).create(vals)
        res.get_default_get_lines()
        return res

    @api.constrains('name')
    def check_unique_name(self):
        for res in self:
            others = [o.id for o in self.env['amh.culture'].search([]) \
                      if o.name.lower() == res.name.lower()]
            if len(others) > 1:
                raise ValidationError('Le nom est unique par culture !')


class CultureLineAMH(models.Model):
    _name = 'amh.culture.line'

    name = fields.Selection(NAME_LINES_CULTURE, string="Designation")
    amh_culture_id = fields.Many2one('amh.culture', string="Culture", required=False, ondelete='cascade')
    amh_culture_prj_id = fields.Many2one('amh.culture', string="Culture.", required=False, ondelete='cascade')
    project_id = fields.Many2one('project.project', string="Projet", required=False, ondelete='cascade')

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
