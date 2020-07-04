# -*- coding: utf-8 -*-

import time
import math
from datetime import datetime

from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class ProductForfait(models.Model):
    _name = 'product.forfait'

    name = fields.Char(string="Nom", required=True)
    designation = fields.Char(string="Designation", required=True)

    tmpl_product_ids = fields.Many2many('product.template', 'forfait_product_rel', 'forfait_id', 'product_id',
                                            string='Articles')

class ObjetSuivi(models.Model):
    _name = 'objet.suivi'

    name = fields.Char("Nom", required=True)

class RelanceInvoiceRec(models.Model):
    _name ="amh.relance.invoice"

    name = fields.Selection([
        ('1', 'Relance 1'),
        ('2', 'Relance 2'),
        ('3', 'Relance 3'),
    ], string='Nom',required=True)
    nb_jours = fields.Integer("Nbr. jours", required=True)
    users_ids = fields.Many2many("res.users", string="Utilisateurs")

class MotifDesap(models.Model):
    _name = "motif.desapar"

    name = fields.Char("Description", rrequired=True)




