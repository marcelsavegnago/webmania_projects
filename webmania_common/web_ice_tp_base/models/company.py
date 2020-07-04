# encoding: utf-8
from odoo import models, api, fields, _
from odoo.exceptions import Warning

import odoo.addons.decimal_precision as dp


class ResCompany(models.Model):
    _inherit = 'res.company'
    _description = 'Company'


    ice = fields.Char(string='ICE', size=15,)
    identifiant_tp = fields.Char(string=u'Identifiant TP', size=64,)
