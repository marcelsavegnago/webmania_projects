# -*- coding: utf-8 -*-

import time
import math

from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _



class ResUsersAMh(models.Model):
    _inherit = "res.users"

    recoi_sms = fields.Boolean(string='Reçoi des SMS Demande', default=False,
                                help="Recevoir des SMS à la validation du demande")
    recoi_sms_som = fields.Boolean(string='Reçoi des SMS Sommeil', default=False,
                               help="Recevoir des SMS à la creation du demande de sommeil")
    recoi_sms_inv = fields.Boolean(string='Reçoi des SMS factures recurrentes', default=False,
                               help="Recevoir des SMS à la creation d'une facture recurrente")
    # TO BE #ignored
    #restrict_locations = fields.Boolean()
    #default_picking_type_ids = fields.Boolean()
    #stock_location_ids = fields.Boolean()

